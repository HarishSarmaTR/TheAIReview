# 🚀 AI Code Review Tool

### This Python-based tool leverages the GitHub API and OpenArena AI to automate code reviews on pull requests. Designed exclusively for Thomson Reuters employees, it enhances the code review process by extracting modified lines, sending them for AI-based analysis, and posting insightful comments and suggestions directly on GitHub PRs.

![image](https://github.com/user-attachments/assets/c0118111-497b-4fe6-a760-37867832717e)


---

# 🛠 Installation

### 1️⃣ Prerequisites

- ### Ensure you have the following installed:

- **Python 3.8+**
- **pip (Python package manager)**
- ### Install pyinstaller and run this:

```
pip install pyinstaller
```
```
pyinstaller --onefile .\AIReview.py
```

- ### Install PyGitHub 

```
pip install PyGithub requests
```

### 2️⃣ Get the Open Arena token

- #### Please refer 👉 [Open Arena Link](https://helix.thomsonreuters.com/static-sites/site-builds/gcs-ml_ai-platform-documentation/ai-platform/09_openarena/api_user_guide.html#step-5-locate-your-esso-token)


### 3️⃣ Create Github Token
- #### Create a github hub token from developer settings 

![image](https://github.com/user-attachments/assets/f7eac2cc-b91a-4cf5-b589-5654ee371283)

---

# ⚙️ Configuration

## Before running the tool, make sure you have:

- GitHub Token: For authentication with the GitHub API

- OpenArena Token: To send modified code for AI-based review

- These credentials must be entered when prompted in the GUI.

---

# 🚀 Usage

## 1. Run the tool:

- python main.py


## 2. Enter the required details in the GUI:

- GitHub Token

- OpenArena Token

- Repository Name (e.g., username/repo)

- Pull Request Number


## 3. Click "Run Code Review" to initiate the process.


## 4. AI-generated comments will be posted directly on the PR.


## 5. Check your PR on GitHub to view the feedback.

---

# 📌 Features

- ✅ Extracts exact modified lines from PR patches
- ✅ Sends changes to OpenArena AI for review
- ✅ Analyzes logic impact, potential issues, and code consistency
- ✅ Posts AI-generated comments on GitHub PR
- ✅ Displays progress and results in a simple Tkinter GUI


---

# 🛠 Troubleshooting

- 🔹 Error: Authentication failed – Ensure your GitHub token has the correct permissions.
- 🔹 Error: AI review failed – Check your OpenArena API token and internet connection.
- 🔹 Comments not appearing on PR? – Verify that the PR number and repository name are correct.

For any issues, feel free to open an issue in the repo.

---

# 🏆 Credits

## Developed by the Ultratax Team, 2025.
- **Kalyani, Kandunuri**
- **Harish Sarma, Velavalapalli**

- Speacial thanks to **Radhika Ramagiri** and **Prasad Kolaparthi** 💖

---
