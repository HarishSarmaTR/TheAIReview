def simple_review_code(diff, openarena_token, log_fn=None):
    """
    A simplified function to send code to OpenArena API for review
    using Claude v4 Sonnet model
    
    Args:
        diff: The code diff to review
        openarena_token: API token for OpenArena
        log_fn: Function to log messages
    
    Returns:
        Tuple of (feedback, cost_usd, total_tokens)
    """
    import requests
    
    def log(msg):
        """Helper to log messages"""
        if log_fn:
            log_fn(msg)
        print(msg)
    
    log("Setting up API request for code review")
    
    headers = {
        'Authorization': f'Bearer {openarena_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "workflow_id": "0a654593-da34-4dfe-a6ed-9c8506e31b73",
        "query": f"""Review the following code changes: {diff}

PROVIDE SEPARATE COMMENTS FOR EACH MODIFIED LINE or logical block from the pull request ONLY where there are actual issues or improvements needed. DO NOT combine all comments into a single block.

Focus ONLY on the following aspects that require attention and don't comment on code that already follows best practices:
1. ACTUAL Logic Errors: Identify faulty logic that could lead to incorrect behavior or bugs
2. Syntax Errors: Point out syntax issues that would cause compilation failures
3. Potential Runtime Errors: Flag operations that could lead to crashes, memory leaks, or unexpected behavior
4. Security Vulnerabilities: Highlight code that could introduce security risks
5. Performance Issues: Identify inefficient implementations that could cause performance problems
6. Serious Maintainability Issues: Comment only on major readability or maintainability concerns

DO NOT COMMENT ON:
1. Code that already follows best practices (like already using const)
2. Trivial stylistic issues
3. Include statements or namespaces unless they cause actual issues
4. Variable names unless they are misleading or confusing
5. Test fixtures or macro definitions in test files unless they're broken
6. Things that are just working as expected and don't need improvement

IMPORTANT FORMATTING: For each ACTUAL issue found, write a separate paragraph starting with 'Line <line_number>: ' followed by your comment.
MAKE SEPARATE COMMENTS for different issues - DO NOT combine multiple issues into one comment.
If a file contains no significant issues, DO NOT add any comments for that file.""",
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

    try:
        log("Sending request to OpenArena API...")
        response = requests.post(
            "https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference",
            headers=headers, 
            json=payload, 
            timeout=60
        )
        
        log(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            ai_response = response.json()
            # Try to get the answer from multiple possible model names
            model_answer = ai_response.get('result', {}).get('answer', {})
            feedback = (
                model_answer.get('openai_gpt-4o', '') or
                model_answer.get('vertexai_gemini-2.5-pro', '') or
                model_answer.get('anthropic_direct.claude-v4-sonnet', '') or
                model_answer.get('vertexai_palm-2', '')
            )
            
            if not feedback:
                log("⚠️ Received empty feedback despite 200 status")
                return "No specific issues detected in the code changes.", 0.0, 0
                
            log("💬 AI Code Review Feedback received.")
            
            # Extract cost information from the response
            cost_info = ai_response.get('result', {}).get('cost', {})
            token_usage = cost_info.get('token_usage', {})
            total_tokens = token_usage.get('total_tokens', 0)
            cost_usd = cost_info.get('cost_usd', 0.0)
            
            log(f"📊 Token usage: {total_tokens} tokens, Est. cost: ${cost_usd:.5f}")
            return feedback, cost_usd, total_tokens
        else:
            log(f"⚠️ API Error: {response.status_code}, {response.text}")
            return f"API Error ({response.status_code}): Could not process review.", 0.0, 0
            
    except Exception as e:
        log(f"🚨 Failed to review code: {str(e)}")
        return f"Error: {str(e)}", 0.0, 0
