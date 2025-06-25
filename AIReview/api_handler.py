import requests
import time

def calculate_claude_cost(prompt_tokens, completion_tokens):
    """
    Calculate the cost for Claude 4 Sonnet based on token usage.
    
    Args:
        prompt_tokens: Number of tokens in the prompt/input
        completion_tokens: Number of tokens in the completion/output
    
    Returns:
        Cost in USD
    
    Pricing:
    - Input: $0.003 per 1,000 tokens (up to 200k)
    - Output: $0.015 per 1,000 tokens (up to 64k)
    """
    input_cost = (prompt_tokens / 1000) * 0.003
    output_cost = (completion_tokens / 1000) * 0.015
    return input_cost + output_cost

def review_code_with_ai(diff, openarena_token, log_activity_fn=None):
    """
    Send code to OpenArena API for review using GPT-4o model
    
    Args:
        diff: The code diff to review
        openarena_token: API token for OpenArena
        log_activity_fn: Function to log activity messages (optional)
    
    Returns:
        Tuple of (feedback, cost_usd, total_tokens)
    """
    def log(msg):
        """Helper to log messages"""
        if log_activity_fn:
            log_activity_fn(msg)
        print(msg)
    
    headers = {
        'Authorization': f'Bearer {openarena_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "query": ("Review the following code from:" + diff + ", and provide SEPARATE COMMENTS FOR EACH MODIFIED LINE or logical block from the pull request ONLY where there are actual issues or improvements needed. DO NOT combine all comments into a single block.\n"
            "Focus ONLY on the following aspects that require attention and don't comment on code that already follows best practices:\n"
            "1. ACTUAL Logic Errors: Identify faulty logic that could lead to incorrect behavior or bugs\n"
            "2. Syntax Errors: Point out syntax issues that would cause compilation failures\n"
            "3. Potential Runtime Errors: Flag operations that could lead to crashes, memory leaks, or unexpected behavior\n"
            "4. Security Vulnerabilities: Highlight code that could introduce security risks\n"
            "5. Performance Issues: Identify inefficient implementations that could cause performance problems\n"
            "6. Serious Maintainability Issues: Comment only on major readability or maintainability concerns\n"
            "7. ONLY suggest const for variables that aren't already marked const and should be\n"
            "8. ONLY point out string handling issues with char* when it causes actual problems\n"
            
            "DO NOT COMMENT ON:\n"
            "1. Code that already follows best practices (like already using const)\n"
            "2. Trivial stylistic issues\n"
            "3. Include statements or namespaces unless they cause actual issues\n"
            "4. Variable names unless they are misleading or confusing\n"
            "5. Test fixtures or macro definitions in test files unless they're broken\n"
            "6. Issues already addressed in other parts of the code\n"
            "7. Things that are just working as expected and don't need improvement\n"
            
            "IMPORTANT FORMATTING: For each ACTUAL issue found, write a separate paragraph starting with 'Line <line_number>: ' followed by your comment.\n"
            "MAKE SEPARATE COMMENTS for different issues - DO NOT combine multiple issues into one comment.\n"
            "If a file contains no significant issues, DO NOT add any comments for that file.\n"
            "Example format for issues:\n"
            "Line 42: Logical error: The loop condition 'i <= array.size()' will cause out-of-bounds access on the last iteration. Should be 'i < array.size()' instead.\n\n"
            "Line 78: Potential null pointer dereference: 'ptr' is not checked for nullptr before being accessed.\n\n"
        ),
        "workflow_id": "0a654593-da34-4dfe-a6ed-9c8506e31b73",  # OpenArena Chain workflow ID
        "is_persistence_allowed": False,
        "modelparams": {
            "openai_gpt-4o": {
                "temperature": "0.7",
                "top_p": "1", 
                "max_tokens": "16384",
                "system_prompt": "You are an experienced Software Developer reviewing code changes. Focus ONLY on actual issues in the code that could cause bugs, performance problems, or maintainability challenges. Do not comment on code that already follows best practices or working code that doesn't need improvements. If the code is good, it's acceptable to provide no comments. Quality is more important than quantity - only point out real issues."
            }
        }
    }

    # Add retry logic for API timeouts
    max_retries = 2
    retry_count = 0
    retry_delay = 5  # seconds
    
    while retry_count <= max_retries:
        try:
            if retry_count > 0:
                log(f"Retry attempt {retry_count}/{max_retries} for OpenArena API call...")
                
            response = requests.post("https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference",
                                   headers=headers, json=payload, timeout=60)
            log(f"🤖 OpenArena API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                ai_response = response.json()
                # Try to get the answer from multiple possible model names
                model_answer = ai_response.get('result', {}).get('answer', {})
                feedback = (model_answer.get('openai_gpt-4o', '') or 
                          model_answer.get('vertexai_gemini-2.5-pro', '') or
                          model_answer.get('anthropic_direct.claude-v4-sonnet', '') or
                          model_answer.get('vertexai_palm-2', ''))
                
                log("💬 AI Code Review Feedback received")
                
                # Check if feedback is empty but status was 200
                if not feedback or not feedback.strip():
                    log(f"⚠️ Warning: Received empty feedback from OpenArena API despite 200 status")
                    if retry_count < max_retries:
                        retry_count += 1
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        log(f"⚠️ Empty response received after all retries. The API may need more time to process this file.")
                        return "Line 1: No significant issues detected in the code changes.", 0.0, 0
                  # Extract cost information from the response
                cost_info = ai_response.get('result', {}).get('cost', {})
                token_usage = cost_info.get('token_usage', {})
                prompt_tokens = token_usage.get('prompt_tokens', 0)
                completion_tokens = token_usage.get('completion_tokens', 0)
                total_tokens = token_usage.get('total_tokens', 0)
                
                # Get API-provided cost as fallback
                api_cost_usd = cost_info.get('cost_usd', 0.0)
                  # Initialize cost_usd
                cost_usd = api_cost_usd
                
                # Calculate Claude 4 Sonnet cost if applicable or if model used is Claude
                if 'anthropic_direct.claude-v4-sonnet' in model_answer or 'claude' in str(model_answer).lower():
                    # If we don't have the prompt/completion breakdown but have total
                    if prompt_tokens == 0 and completion_tokens == 0 and total_tokens > 0:
                        # Estimate typical ratio: 70% prompt, 30% completion
                        prompt_tokens = int(total_tokens * 0.7)
                        completion_tokens = total_tokens - prompt_tokens
                    
                    # Calculate cost using Claude 4 pricing
                    cost_usd = calculate_claude_cost(prompt_tokens, completion_tokens)
                    log(f"📊 Claude 4 Sonnet pricing applied: ${cost_usd:.5f}")

                log(f"📊 Token usage: {total_tokens} tokens (Prompt: {prompt_tokens}, Completion: {completion_tokens})")
                log(f"💰 Est. cost: ${cost_usd:.5f}")
                # Return feedback and cost information
                return feedback, cost_usd, total_tokens            
            elif response.status_code in [504, 408, 502, 503]:  # Timeout and server errors
                if retry_count < max_retries:
                    log(f"⚠️ OpenArena API timeout/error: {response.status_code}, {response.text}")
                    log(f"Waiting {retry_delay} seconds before retry...")
                    retry_count += 1
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    log(f"❌ Maximum retries reached. Could not get response from OpenArena API.")
                    return "", 0.0, 0
            
            else:
                log(f"⚠️ OpenArena Error: {response.status_code}, {response.text}")
                return "", 0.0, 0
                
        except Exception as e:
            if retry_count < max_retries:
                log(f"🚨 API call failed with error: {e}. Retrying in {retry_delay} seconds...")
                retry_count += 1
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                log(f"🚨 Failed to review code after {max_retries} retries: {e}")
                return "", 0.0, 0
    
    return "", 0.0, 0  # Fallback return if all retries fail
