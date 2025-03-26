import tkinter as tk
from tkinter import messagebox
import re
import requests
from github import Github

# Global variables to store tokens during the session
github_token = None
openarena_token = None

# 🎯 Extract exact modified lines from the patch
def get_modified_lines_from_patch(patch_text):
    modified_lines = {}
    current_new_line = None

    for line in patch_text.split('\n'):
        hunk_match = re.match(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
        if hunk_match:
            current_new_line = int(hunk_match.group(2))
            continue

        if current_new_line is None:
            continue

        if line.startswith('+') and not line.startswith('+++'):
            # ✅ Added line
            modified_lines[current_new_line] = line[1:].strip()
            current_new_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            # ❌ Removed line
            modified_lines[-current_new_line] = line[1:].strip()
        else:
            if line and not line.startswith('@@'):
                current_new_line += 1

    return modified_lines  # Returns {line_number: "line_content"}

# 🚀 Send modified lines to AI for review
def review_code(diff, openarena_token):
    headers = {
        'Authorization': f'Bearer {openarena_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "query": (
            "Review the following code from:" +diff+ ", and provide detailed comment for each modified line. " "\n"
            "For each changed line, consider the following aspects:\n"
            "1. Logic Impact: Does the change alter the program's intended behavior?\n"
            "2. Potential Issues: Identify any syntax errors, typos, or unintended consequences.\n"
            "3. Code Consistency: Ensure the change aligns with existing coding patterns.\n"
            "4. For each comment, explain what the code does and suggest a fix if necessary. "
            "5. Recommendations: Suggest improvements if necessary.\n"
            "6. For removed lines, explain why the code might have been removed and its impact.\n"
            "Do not include the original or modified lines in the comments. Also update everything in one comment which is related to the issue.\n"
            "Provide the comment in the format 'Line <line_number>: <comment>' with suggestion:.\n\n"
        ),
        "workflow_id": "80f448d2-fd59-440f-ba24-ebc3014e1fdf",
        "is_persistence_allowed": False,
        "modelparams": {
            "openai_gpt-4": {
                "system_prompt": (
                    "You are an experienced Software Developer. You have been assigned to review a PR that contains changes to the codebase. "
                    "Analyze the modified lines and give comments for potential issues with exact line numbers. "
                    "For each comment, explain what the code does and suggest a fix if necessary."
                )
            }
        }
    }

    try:
        response = requests.post("https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference",
                                 headers=headers, json=payload)
        print(f"🤖 OpenArena API Response Status: {response.status_code}")

        if response.status_code == 200:
            ai_response = response.json()
            feedback = ai_response.get('result', {}).get('answer', {}).get('openai_gpt-4-turbo', 'system_prompt')
            print("💬 AI Code Review Feedback:", feedback)
            return feedback
        else:
            print(f"⚠️ OpenArena Error: {response.status_code}, {response.text}")
            return ""
    except Exception as e:
        print(f"🚨 Failed to review code: {e}")
        return ""

# 💬 Post comments on GitHub PR
def post_comments_on_pr(pr, comments, filename, modified_lines):
    added_comments = set()
    commits = list(pr.get_commits())
    latest_commit = commits[-1]

    for line_content in comments:
        line_content = line_content.strip()
        if not line_content:
            continue

        matches = re.findall(r'\d+', line_content)
        if not matches:
            continue

        line_position = int(matches[0])

        # Determine the side of the comment
        side = "RIGHT" if line_position > 0 else "LEFT"

        # Ensure valid modified line for added lines
        if side == "RIGHT" and line_position not in modified_lines:
            print(f"⚠️ Skipping invalid line {line_position} for {filename}. Not in diff.")
            continue

        if line_content in added_comments:
            continue

        try:
            pr.create_review_comment(
                body=line_content,
                commit=latest_commit,
                path=filename,
                line=line_position,
                side="LEFT"
            )
            added_comments.add(line_content)
            print(f"✅ Commented on PR #{pr.number}, line {line_position}: {line_content}")
        except Exception as e:
            print(f"🚨 Error posting comment on line {line_position}: {e}")

    return added_comments

def main(repo_name, pr_number):
    try:
        global github_token, openarena_token
        if not github_token or not openarena_token:
            raise ValueError("Tokens must be provided.")

        loading_label.config(text="Processing...", fg="blue")
        root.update_idletasks()

        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        all_added_comments = set()
        for file in pr.get_files():
            diff = file.patch
            print(f"\n🔍 Reviewing the code for file: {file.filename}\n{'-'*60}")

            # Extract exact modified lines
            modified_lines = get_modified_lines_from_patch(diff)

            # Convert extracted lines into a formatted string for AI review
            diff_text = "\n".join([f"{line_num}: {content}" for line_num, content in modified_lines.items()])
            
            # 🚀 Send modified lines to AI
            comments = review_code(diff_text, openarena_token)
            if not comments:
                print(f"❌ No AI feedback for {file.filename}")
                continue

            # 💬 Post AI feedback as PR comments
            comment_lines = comments.split('\n')
            added_comments = post_comments_on_pr(pr, comment_lines, file.filename, modified_lines)
            all_added_comments.update(added_comments)

        if all_added_comments:
            pr.create_issue_comment(
                "✅ Reviewed code and added AI-generated comments. Please check and resolve."
            )
            print(f"\n🚀 Posted an issue comment on PR #{pr.number}.\n")

        loading_label.config(text="Completed", fg="green")
        print("🎉 Code review by AI has been completed. Check PR for details.")
        messagebox.showinfo("Success", "Code review completed successfully!")

    except Exception as e:
        loading_label.config(text="Error", fg="red")
        print(f"🚨 Error in main function: {e}")
        messagebox.showerror("Error", f"Failed to complete code review: {e}")

def run_code_review():
    global github_token, openarena_token
    github_token = github_token_entry.get()
    openarena_token = openarena_token_entry.get()
    repo_name = repo_name_entry.get()
    pr_number = pr_number_entry.get()

    if not (github_token and openarena_token and repo_name and pr_number):
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    main(repo_name, pr_number)

# Create the main Tkinter window
root = tk.Tk()
root.title("Code Review Tool")
root.geometry("1050x500")  # Set window size

# Set background color and font styles
root.configure(bg="#f0f0f0")

header_label = tk.Label(root, text="AI Code Review Tool", font=("Helvetica", 16, "bold"), bg="#f0f0f0", fg="#333")
header_label.pack(pady=10)

# Create input fields and labels with styling
tk.Label(root, text="GitHub Token", font=("Helvetica", 12), bg="#f0f0f0").pack()
github_token_entry = tk.Entry(root, show="*", width=40)
github_token_entry.pack(pady=5)

tk.Label(root, text="OpenArena Token", font=("Helvetica", 12), bg="#f0f0f0").pack()
openarena_token_entry = tk.Entry(root, show="*", width=40)
openarena_token_entry.pack(pady=5)

tk.Label(root, text="Repository Name", font=("Helvetica", 12), bg="#f0f0f0").pack()
repo_name_entry = tk.Entry(root, width=40)
repo_name_entry.pack(pady=5)

tk.Label(root, text="Pull Request Number", font=("Helvetica", 12), bg="#f0f0f0").pack()
pr_number_entry = tk.Entry(root, width=40)
pr_number_entry.pack(pady=5)

# Create a button with styling
review_button = tk.Button(root, text="Run Code Review", command=run_code_review, bg="#4CAF50", fg="white", font=("Helvetica", 12), width=20)
review_button.pack(pady=20)

# Create a loading indicator
loading_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f0f0", fg="blue")
loading_label.pack(pady=5)

# Add additional information with styling
footer_label = tk.Label(root, text="Built by Ultratax Team, 2025", font=("Arial", 10), bg="#f0f0f0")
footer_label.pack(side="bottom", pady=10)

# Run the Tkinter event loop
root.mainloop()