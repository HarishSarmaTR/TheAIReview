def process_large_diff_in_chunks(diff, openarena_token, log_fn=None, max_chunk_size=5000):
    """
    Process large diffs in chunks to handle file size limitations
    
    Args:
        diff: The large diff to process
        openarena_token: API token for OpenArena
        log_fn: Function to log messages
        max_chunk_size: Maximum size of each chunk
    
    Returns:
        Tuple of (combined_feedback, total_cost, total_tokens)
    """
    def log(msg):
        if log_fn:
            log_fn(msg)
        print(msg)
    
    log(f"Processing large diff in chunks (size: {len(diff)} chars)")
    
    # Split diff into logical chunks
    lines = diff.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        
        # If adding this line would exceed chunk size, save current chunk
        if current_size + line_size > max_chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size
    
    # Add remaining lines as last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    log(f"Split into {len(chunks)} chunks")
    
    # Process each chunk
    all_feedback = []
    total_cost = 0.0
    total_tokens = 0
    
    for i, chunk in enumerate(chunks, 1):
        log(f"Processing chunk {i}/{len(chunks)}")
        
        try:
            feedback, cost, tokens = simple_review_code(chunk, openarena_token, log_fn, max_chunk_size * 2)  # Prevent infinite recursion
            
            if feedback and feedback.strip():
                all_feedback.append(f"[Chunk {i}/{len(chunks)}]\n{feedback}")
            
            total_cost += cost
            total_tokens += tokens
            
        except Exception as e:
            log(f"Error processing chunk {i}: {e}")
            continue
    
    # Combine all feedback
    combined_feedback = '\n\n'.join(all_feedback) if all_feedback else "No issues found in the large file review."
    
    log(f"Completed chunked processing: {len(all_feedback)} chunks with feedback")
    return combined_feedback, total_cost, total_tokens

def simple_review_code(diff, openarena_token, log_fn=None, max_chunk_size=5000):
    """
    A simplified function to send code to OpenArena API for review
    using Claude v4 Sonnet model with support for large files via chunking
    
    Args:
        diff: The code diff to review
        openarena_token: API token for OpenArena
        log_fn: Function to log messages
        max_chunk_size: Maximum size of each chunk for large files
    
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
    
    # Check if diff is too large and needs chunking
    if len(diff) > max_chunk_size:
        log(f"Large diff detected ({len(diff)} chars), processing in chunks")
        return process_large_diff_in_chunks(diff, openarena_token, log_fn, max_chunk_size)
    
    headers = {
        'Authorization': f'Bearer {openarena_token}',
        'Content-Type': 'application/json'
    }
    
    # Enhanced prompt for better handling of new files and large changes
    enhanced_prompt = f"""Review the following code changes: {diff}

IMPORTANT GUIDELINES:
- For NEW FILES: Focus on overall architecture, major design issues, and critical problems only
- For LARGE FILES: Prioritize security vulnerabilities, logic errors, and performance issues
- For SMALL CHANGES: Provide detailed feedback on specific issues

CRITICAL FORMAT REQUIREMENT: ONLY provide comments for SPECIFIC LINES with actual issues. Each comment MUST start with 'Line X: ' where X is the exact line number from the diff.

Focus ONLY on the following aspects that require attention and don't comment on code that already follows best practices:
1. ACTUAL Logic Errors: Identify faulty logic that could lead to incorrect behavior or bugs
2. Syntax Errors: Point out syntax issues that would cause compilation failures
3. Potential Runtime Errors: Flag operations that could lead to crashes, memory leaks, or unexpected behavior
4. Security Vulnerabilities: Highlight code that could introduce security risks
5. Performance Issues: Identify inefficient implementations that could cause performance problems
6. Serious Maintainability Issues: Comment only on major readability or maintainability concerns

DO NOT COMMENT ON:
1. Code that already follows best practices (like adding const qualifiers)
2. Trivial stylistic issues
3. Include statements or namespaces unless they cause actual issues
4. Variable names unless they are misleading or confusing
5. Test fixtures or macro definitions in test files unless they're broken
6. Things that are just working as expected and don't need improvement
7. General observations about the code quality

IMPORTANT FORMATTING: 
- Each comment MUST start with 'Line <specific_line_number>: ' 
- DO NOT use general comments or observations
- DO NOT comment on multiple lines at once
- If no specific issues are found, provide NO comments
- Quality over quantity - only report actual problems"""
    
    payload = {
        "workflow_id": "0a654593-da34-4dfe-a6ed-9c8506e31b73",
        "query": enhanced_prompt,
        "is_persistence_allowed": False,
        "modelparams": {
            "openai_gpt-4o": {
                "temperature": "0.7",
                "top_p": "1",
                "max_tokens": "16384",
                "system_prompt": "You are an experienced Software Developer reviewing code changes. Focus ONLY on actual issues in the code that could cause bugs, performance problems, or maintainability challenges. Do not comment on code that already follows best practices or working code that doesn't need improvements. If the code is good, it's acceptable to provide no comments. Quality is more important than quantity - only point out real issues. For large files or new files, prioritize the most critical issues."
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
