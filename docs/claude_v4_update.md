# AI Review Tool Update - Claude v4 Support

## What's New
- Added support for Claude v4 Sonnet via OpenArena API
- Improved token handling and error recovery
- Fixed "Invalid Token" errors with new token migration and backup

## Model Parameters for Claude v4
The tool now uses the following parameters with the Claude v4 model:
```json
{
    "workflow_id": "7c41c3ab-c214-4394-ba38-9da289975d85",
    "query": "Review the following code...",
    "is_persistence_allowed": false,
    "modelparams": {
        "anthropic_direct.claude-v4-sonnet": {
            "temperature": "0.7",
            "top_p": "1",
            "max_tokens": "16384",
            "top_k": "250",
            "system_prompt": "You are an experienced Software Developer...",
            "enable_reasoning": "true",
            "budget_tokens": "4096"
        }
    }
}
```

## Testing the API
A test script is included to validate the Claude v4 API connection:
1. Run `test_api.bat` to execute a simple test
2. Check the output for the AI's response

## Troubleshooting
If you encounter "Invalid Token" errors:
1. The tool will automatically back up corrupted token files as `tokens.txt.bak`
2. Re-enter your tokens and save them again
3. If problems persist, delete the `encryption.key` file and restart the application

For any other issues, please contact support.
