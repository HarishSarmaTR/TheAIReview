import argparse
import requests
import time
import os
import json

def review_code(diff_text, openarena_token):
    """
    Send code to OpenArena API for review using Claude v4 Sonnet model
    
    Args:
        diff_text: The code diff to review
        openarena_token: API token for OpenArena
    
    Returns:
        Tuple of (feedback, cost_usd, total_tokens)
    """
    headers = {
        'Authorization': f'Bearer {openarena_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "workflow_id": "0a654593-da34-4dfe-a6ed-9c8506e31b73",
        "query": "Review the following code from:" + diff_text,
        "is_persistence_allowed": False,
        "modelparams": {
            "anthropic_direct.claude-v4-sonnet": {
                "temperature": "0.7",
                "top_p": "1",
                "max_tokens": "16384",
                "top_k": "250",
                "system_prompt": "You are an experienced Software Developer analyzing code changes.",
                "enable_reasoning": "true",
                "budget_tokens": "4096"
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
                print(f"Retry attempt {retry_count}/{max_retries} for OpenArena API call...")
                
            response = requests.post("https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference",
                                   headers=headers, json=payload, timeout=60)
            print(f"OpenArena API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Try to get the answer from multiple possible model names
                model_answer = ai_response.get('result', {}).get('answer', {})
                feedback = (model_answer.get('anthropic_direct.claude-v4-sonnet', '') or 
                          model_answer.get('vertexai_gemini-2.5-pro', '') or
                          model_answer.get('openai_gpt-4o', '') or 
                          model_answer.get('vertexai_palm-2', ''))
                
                print("AI Code Review Feedback received")
                
                # Extract cost information from the response
                cost_info = ai_response.get('result', {}).get('cost', {})
                token_usage = cost_info.get('token_usage', {})
                total_tokens = token_usage.get('total_tokens', 0)
                cost_usd = cost_info.get('cost_usd', 0.0)
                
                print(f"Token usage: {total_tokens} tokens, Est. cost: ${cost_usd:.5f}")
                return feedback, cost_usd, total_tokens
                
            elif response.status_code in [504, 408, 502, 503]:  # Timeout and server errors
                if retry_count < max_retries:
                    print(f"OpenArena API timeout/error: {response.status_code}, {response.text}")
                    print(f"Waiting {retry_delay} seconds before retry...")
                    retry_count += 1
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"Maximum retries reached. Could not get response from OpenArena API.")
                    return "", 0.0, 0
            
            else:
                print(f"OpenArena Error: {response.status_code}, {response.text}")
                return "", 0.0, 0
                
        except Exception as e:
            if retry_count < max_retries:
                print(f"API call failed with error: {e}. Retrying in {retry_delay} seconds...")
                retry_count += 1
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"Failed to review code after {max_retries} retries: {e}")
                return "", 0.0, 0
    
    return "", 0.0, 0  # Fallback return if all retries fail

def main():
    parser = argparse.ArgumentParser(description='Test OpenArena API with Claude v4 model')
    parser.add_argument('--text', type=str, default="Print hello world", help='Text to send for review')
    args = parser.parse_args()
    
    # Get token from environment or tokens.txt
    openarena_token = os.environ.get('OPENARENA_TOKEN')
    if not openarena_token:
        try:
            with open("tokens.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    openarena_token = lines[1].strip()
        except Exception as e:
            print(f"Error loading token: {e}")
            return
    
    if not openarena_token:
        print("No OpenArena token found. Please provide it via environment variable OPENARENA_TOKEN")
        return
        
    feedback, cost, tokens = review_code(args.text, openarena_token)
    print(f"\nFeedback received:\n{feedback}")
    print(f"Cost: ${cost:.5f} for {tokens} tokens")

if __name__ == "__main__":
    main()
