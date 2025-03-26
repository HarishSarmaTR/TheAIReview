# TheAIReview

---

🚀 AI Code Review Tool

A Python-based tool that leverages GitHub API and OpenArena AI to automate code reviews on pull requests. This tool extracts modified lines, sends them for AI-based review, and posts comments on GitHub PRs with insights and suggestions.


---

🛠 Installation

1️⃣ Prerequisites

Ensure you have the following installed:

Python 3.8+

pip (Python package manager)

GitHub Personal Access Token (with repo access)

OpenArena API Token (for AI-based review)


2️⃣ Clone the Repository

git clone https://github.com/<your-username>/<your-repo>.git  
cd <your-repo>

3️⃣ Install Dependencies

pip install -r requirements.txt


---

⚙️ Configuration

Before running the tool, make sure you have:

GitHub Token: For authentication with the GitHub API

OpenArena Token: To send modified code for AI-based review


These credentials must be entered when prompted in the GUI.


---

🚀 Usage

1. Run the tool:

python main.py


2. Enter the required details in the GUI:

GitHub Token

OpenArena Token

Repository Name (e.g., username/repo)

Pull Request Number



3. Click "Run Code Review" to initiate the process.


4. AI-generated comments will be posted directly on the PR.


5. Check your PR on GitHub to view the feedback.




---

📌 Features

✅ Extracts exact modified lines from PR patches
✅ Sends changes to OpenArena AI for review
✅ Analyzes logic impact, potential issues, and code consistency
✅ Posts AI-generated comments on GitHub PR
✅ Displays progress and results in a simple Tkinter GUI


---

🏗️ Contributing

We welcome contributions! If you’d like to improve the tool:

1. Fork the repository


2. Create a new branch (git checkout -b feature-name)


3. Make your changes & commit (git commit -m "Your message")


4. Push to GitHub (git push origin feature-name)


5. Create a pull request 🚀




---

🛠 Troubleshooting

🔹 Error: Authentication failed – Ensure your GitHub token has the correct permissions.
🔹 Error: AI review failed – Check your OpenArena API token and internet connection.
🔹 Comments not appearing on PR? – Verify that the PR number and repository name are correct.

For any issues, feel free to open an issue in the repo.


---

📜 License

This project is licensed under the MIT License.


---

🏆 Credits

Developed by the Ultratax Team, 2025.


---
