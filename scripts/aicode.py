import os
import requests
import re

def fetch_diff(pr_url, github_token):
    """Fetches the diff of the pull request from GitHub."""
    headers = {'Authorization': f'token {github_token}', 'Accept': 'application/vnd.github.v3+json'}
    try:
        response = requests.get(f"{pr_url}/files", headers=headers)
        response.raise_for_status()
        files = response.json()
        diff = ''.join(file.get('patch', '') for file in files)
        return files, diff
    except requests.RequestException as e:
        raise Exception(f"Error fetching PR diff: {e}")

def review_code(diff, open_arena_token):
    """Sends the diff to the OpenAI API for review and retrieves comments."""
    headers = {'Authorization': f'Bearer {open_arena_token}', 'Content-Type': 'application/json'}
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": "You are a code reviewer."},
            {"role": "user", "content": f"Review the following code diff and suggest improvements with line numbers:\n{diff}"}
        ],
        "max_tokens": 800,
        "temperature": 0.5
    }

    try:
        response = requests.post("https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference", headers=headers, json=data)
        print("Response Headers:", response.headers)

        if response.status_code == 200:
            ai_response = response.json()
            print(f"OpenAI API Usage: {ai_response.get('usage', {})}")
            return ai_response['choices'][0]['message']['content'].strip()
        else:
            raise Exception(f"OpenAI Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Failed to review code: {e}")
        return ""

def parse_ai_response(ai_response):
    """Extract line-specific comments from the AI response."""
    comments = []
    lines = ai_response.split('\n')
    for line in lines:
        match = re.search(r'Line (\d+): (.+)', line)
        if match:
            line_number = int(match.group(1))
            comment = match.group(2)
            comments.append((line_number, comment))
    return comments

def post_line_comment(pr_number, file_path, line_number, comment, github_token):
    """Posts a comment on a specific line of a pull request."""
    try:
        repo = os.getenv('GITHUB_REPOSITORY')
        comments_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
        headers = {'Authorization': f'token {github_token}', 'Content-Type': 'application/json'}
        data = {
            "body": comment,
            "commit_id": "",  # Commit ID is needed here
            "path": file_path,
            "line": line_number,
            "side": "RIGHT"
        }
        response = requests.post(comments_url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Comment posted on line {line_number} of {file_path}.")
    except requests.RequestException as e:
        raise Exception(f"Error posting line comment: {e}")

def validate_environment_variables(*vars):
    """Validates the presence of required environment variables."""
    missing_vars = [var for var in vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def main():
    """Main function to fetch PR diff, review code, and post comments."""
    try:
        validate_environment_variables("GITHUB_PR_URL", "GITHUB_TOKEN", "OPEN_ARENA_TOKEN")
        pr_url = os.getenv("GITHUB_PR_URL")
        github_token = os.getenv("GITHUB_TOKEN")
        open_arena_token = os.getenv("OPEN_ARENA_TOKEN")

        print(f"PR URL: {pr_url}")
        print(f"GitHub Token: {'Provided' if github_token else 'Missing'}")
        print(f"OpenAI API Key: {'Provided' if open_arena_token else 'Missing'}")

        # Fetch PR diff
        print("Fetching PR diff...")
        files, diff = fetch_diff(pr_url, github_token)

        # Review code
        print("Sending diff to OpenAI for review...")
        ai_review = review_code(diff, open_arena_token)
        if not ai_review:
            ai_review = "No significant suggestions provided."

        # Parse AI response for line-specific comments
        comments = parse_ai_response(ai_review)

        # Post line-specific comments
        for file in files:
            for line_number, comment in comments:
                post_line_comment(pr_url.split('/')[-1], file['filename'], line_number, comment, github_token)

        print("AI review process completed successfully.")

    except EnvironmentError as env_err:
        print(f"Environment Error: {env_err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
