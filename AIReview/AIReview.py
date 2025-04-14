import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import re
import requests
import webbrowser
from github import Github

# Global variables to store tokens during the session
github_token = None
openarena_token = None

TOKEN_FILE = "tokens.txt"


def open_openarena_link(event):
    """Open the OpenArena link in the default web browser."""
    webbrowser.open("https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/8556ba87-acf8-4049-98a3-fc62a300656c")

def show_info(info_text):
    """Display information about a section."""
    messagebox.showinfo("Information", info_text)

def create_round_info_button(parent, row, column, info_text):
    """Helper function to create a round info button using a Canvas."""
    canvas = tk.Canvas(parent, width=20, height=20, bg="#f0f0f0", highlightthickness=0)
    canvas.create_oval(2, 2, 18, 18, fill="#0000FF")
    canvas.create_text(10, 10, text="i", fill="white", font=("Helvetica", 8, "bold"))
    canvas.grid(row=row, column=column, padx=5)
    canvas.bind("<Button-1>", lambda e: show_info(info_text))

def load_tokens():
    """Load GitHub and OpenArena tokens from a file."""
    global github_token, openarena_token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            tokens = file.readlines()
            if len(tokens) >= 2:
                github_token = tokens[0].strip()
                openarena_token = tokens[1].strip()
                github_token_entry.insert(0, github_token)
                openarena_token_entry.insert(0, openarena_token)

def save_tokens():
    """Save tokens to a file."""
    global github_token, openarena_token
    github_token = github_token_entry.get()
    openarena_token = openarena_token_entry.get()
    with open(TOKEN_FILE, 'w') as file:
        file.write(f"{github_token}\n{openarena_token}\n")
    messagebox.showinfo("Success", "Tokens saved successfully!")

def clear_tokens():
    """Clear the token entries."""
    github_token_entry.delete(0, tk.END)
    openarena_token_entry.delete(0, tk.END)

def run_code_review():
    global github_token, openarena_token
    github_token = github_token_entry.get()
    openarena_token = openarena_token_entry.get()
    repo_name = repo_name_entry.get()
    pr_number = pr_number_entry.get()

    if not (github_token and openarena_token and repo_name and pr_number):
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    status_message.set("Running code review...")
    root.update_idletasks()
    main(repo_name, pr_number)

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
            "Review the following code from:" + diff + ", and provide detailed comment for each modified line. " "\n"
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

        status_message.set("Processing...")
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

        status_message.set("Completed")
        print("🎉 Code review by AI has been completed. Check PR for details.")
        messagebox.showinfo("Success", "Code review completed successfully!")

    except Exception as e:
        status_message.set("Error")
        print(f"🚨 Error in main function: {e}")
        messagebox.showerror("Error", f"Failed to complete code review: {e}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Code Review Tool")
root.geometry("770x450")
root.configure(bg="#f0f0f0")

# Disable window resizing (remove maximize button)
root.resizable(False, False)

# Create a frame for the image/design
image_frame = tk.Frame(root, bg="#f0f0f0", width=100, height=200)
image_frame.grid(row=0, column=0, sticky="nswe")

# Create a frame for PR details and input fields
details_frame = tk.Frame(root, bg="#f0f0f0")
details_frame.grid(row=0, column=1, sticky="nswe")

# Configure grid weights
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)

# Resize image to fit the image frame
try:
    logo_image = Image.open(r"C:\Users\6126175\TheAIReview\images\bot.JPG")
    print("Image opened successfully.")
    # Resize the image to fill the image_frame
    logo_image = logo_image.resize((350, 500), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(image_frame, image=logo_photo, bg="#f0f0f0")
    logo_label.image = logo_photo
    logo_label.pack(expand=True, fill="both")
except Exception as e:
    print(f"Error loading image: {e}")

# Create a frame for PR details and input fields
details_frame = tk.Frame(root, bg="#f0f0f0")
details_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

# Add a header in the details frame
header_label = tk.Label(details_frame, text="🤖 AI Code Review Tool", font=("Helvetica", 16, "bold"), bg="#f0f0f0", fg="#333")
header_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

# Create input fields and labels with info buttons in the details frame
tk.Label(details_frame, text="Enter GitHub Token", font=("Helvetica", 10), bg="#f0f0f0").grid(row=1, column=0, sticky='w', padx=10)
github_token_entry = tk.Entry(details_frame, show="*", width=25)
github_token_entry.grid(row=1, column=1, pady=5, padx=10)
create_round_info_button(details_frame, 1, 2, "Enter your GitHub personal access token here. This is required for accessing GitHub APIs.")

tk.Label(details_frame, text="Enter OpenArena Token", font=("Helvetica", 10), bg="#f0f0f0").grid(row=2, column=0, sticky='w', padx=10)
openarena_token_entry = tk.Entry(details_frame, show="*", width=25)
openarena_token_entry.grid(row=2, column=1, pady=5, padx=10)
create_round_info_button(details_frame, 2, 2, "Enter your OpenArena token here. This is used for authenticating AI API requests.")

# Add the OpenArena link below the OpenArena Token input
openarena_link = tk.Label(details_frame, text="OpenArena Platform Link", font=("Helvetica", 10, "underline"), bg="#f0f0f0", fg="blue", cursor="hand2")
openarena_link.grid(row=3, column=0, columnspan=3, pady=(0, 10), padx=10, sticky='w')
openarena_link.bind("<Button-1>", open_openarena_link)

tk.Label(details_frame, text="Enter Repository Name", font=("Helvetica", 10), bg="#f0f0f0").grid(row=4, column=0, sticky='w', padx=10)
repo_name_entry = tk.Entry(details_frame, width=25)
repo_name_entry.grid(row=4, column=1, pady=5, padx=10)
create_round_info_button(details_frame, 4, 2, "Enter the full repository name in the format 'owner/repo'. This is required to identify the repository on GitHub.")

tk.Label(details_frame, text="Enter PullRequest No.", font=("Helvetica", 10), bg="#f0f0f0").grid(row=5, column=0, sticky='w', padx=10)
pr_number_entry = tk.Entry(details_frame, width=25)
pr_number_entry.grid(row=5, column=1, pady=5, padx=10)
create_round_info_button(details_frame, 5, 2, "Enter the number of the pull request you want to review. This identifies the specific PR on GitHub.")

# Create small buttons for saving and clearing tokens
button_frame = tk.Frame(details_frame, bg="#f0f0f0")
button_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10)

save_button = tk.Button(button_frame, text="Save", command=save_tokens, bg="#FFFFFF", fg="black", font=("Helvetica", 10))
save_button.pack(side="left", padx=5)

clear_button = tk.Button(button_frame, text="Clear", command=clear_tokens, bg="#f44336", fg="white", font=("Helvetica", 10))
clear_button.pack(side="left", padx=5)

# Create a button to run the code review
review_button = tk.Button(details_frame, text="Run Code Review", command=run_code_review, bg="#4CAF50", fg="white", font=("Helvetica", 10), width=20)
review_button.grid(row=7, column=0, columnspan=3, pady=20)

# Create a message box at the bottom for status updates
status_message = tk.StringVar()
status_label = tk.Label(details_frame, textvariable=status_message, font=("Helvetica", 12), bg="#f0f0f0", fg="blue")
status_label.grid(row=8, column=0, columnspan=3, pady=5)

# Add additional information in the details frame at the bottom
footer_label = tk.Label(details_frame, text="Built by Ultratax Team, 2025", font=("Arial", 10), bg="#f0f0f0")
footer_label.grid(row=10, column=0, columnspan=3, pady=10, sticky='s')

# Load tokens on startup
load_tokens()

# Configure grid weights for resizing
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_rowconfigure(0, weight=1)

# Run the Tkinter event loop
root.mainloop()