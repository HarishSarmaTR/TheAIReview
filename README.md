# 🤖 AI Code Review Tool

### This Python-based tool leverages the GitHub API and OpenArena AI to automate code reviews on pull requests. Designed exclusively for Thomson Reuters employees, it enhances the code review process by extracting modified lines, sending them for AI-based analysis, and posting insightful comments and suggestions directly on GitHub PRs.

![image](https://github.com/user-attachments/assets/440beffb-aa4b-4593-98b4-e9988e249b20)

---

# 🛠 Installation

### 1️⃣ Prerequisites

- ### Ensure you have the following installed:

# Windows
## Download Python:
- Visit the [official Python website](https://www.python.org/downloads/) and download the latest version of Python 3.8+.
Run the installer. Ensure you check the box that says "Add Python to PATH" during installation.

## Install pip:

- Pip is automatically installed with Python 3.8+. You can verify the installation by opening Command Prompt and typing:
```
python --version
```
```
pip --version
```

- If pip is not installed, you can manually install it by downloading the get-pip.py script from here and running:
```
python get-pip.py
```
### ⚠️ NOTE : Install pyinstaller and run this if any changes made in the code logic:

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
#### Generate a GitHub Token:
- Navigate to the developer settings on GitHub and create a token. Please choose the "Classic token" option.

#### Ensure the Following Options are Selected:
![image](https://github.com/user-attachments/assets/c035e1ed-87e5-4a3e-b93c-1472c32559ee)
![image](https://github.com/user-attachments/assets/7a2c765c-09fd-4d70-b319-67614893f4dd)
![image](https://github.com/user-attachments/assets/777acef3-f7de-4efa-81e7-337c559bab69)

---

# ⚙️ Configuration

### ❗ Before running the tool, make sure you have:

- GitHub Token: For authentication with the GitHub API

- OpenArena Token: To send modified code for AI-based review

- These credentials must be entered when prompted in the GUI.

---
# 🚀 Usage

### 1. Running the Tool:
- You can find the executable (.exe) for the tool in the **dist folder**. See the examples below:
![image](https://github.com/user-attachments/assets/a3bcf44a-1e95-4ac5-90a9-fee34e2fd8cd)
![image](https://github.com/user-attachments/assets/b02137ec-c499-43e5-b920-63d0a1aa3d05)

### 2. Enter the required details in the GUI:

- GitHub Token

- OpenArena Token

- Repository Name (e.g., username/repo)

- Pull Request Number


### 3. Click "Run Code Review" to initiate the process.


### 4. AI-generated comments will be posted directly on the PR.


### 5. Check your PR on GitHub to view the feedback.

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

### Developed by the Ultratax Team, 2025.
- **Kalyani, Kandunuri**
- **Harish Sarma, Velavalapalli**

- Speacial thanks to **Radhika Ramagiri** and **Prasad Kolaparthi** 💖

---

# 📚 Resources Used
- GitHub API Documentation: For understanding how to interact with GitHub programmatically.
- OpenArena API Documentation: For integrating AI-based code analysis.
- Python Official Documentation: For language-specific features and libraries.
- Tkinter Documentation: For creating the GUI interface.
- PyGitHub Documentation: For utilizing GitHub API features.
