# 🤖 AI Email Agent

A fully autonomous AI-powered email assistant that reads your Gmail, intelligently decides whether to reply, generates professional responses using **TinyLlama**, and stores conversation history in **MySQL**.

---

## ✨ Features

- 🔐 **Secure OAuth2 Authentication** (Gmail API)
- 📬 **Real-time Email Scanning** (Checks every minute)
- 🧠 **AI Decision Engine** (TinyLlama via Ollama)
- ✍️ **Professional Reply Generation** (Prompt-engineered)
- 📂 **Draft Creation** (Safe "human-in-the-loop" mode)
- 🗄️ **Persistent Memory** (Stores all interactions in MySQL)
- 🛑 **Spam & Promotional Filtering** (Ignores junk automatically)

---

## 🛠️ Tech Stack

| Component      | Technology            |
| -------------- | --------------------- |
| Language       | Python 3.11           |
| AI Model       | TinyLlama (Ollama)    |
| Email API      | Gmail API             |
| Authentication | OAuth2                |
| Database       | MySQL                 |
| Scheduler      | `schedule` library    |

---

## 📁 Project Structure
Email-agent/
│
├── main.py # Entry point & scheduler
├── config.py # Environment variables
├── database.py # MySQL connection
├── gmail_auth.py # OAuth2 authentication
├── gmail_reader.py # Fetch unread emails
├── gmail_sender.py # Create drafts / send emails
├── llm.py # TinyLlama integration
├── agent.py # Core decision logic
├── memory.py # Store interactions in DB
├── prompts.py # AI prompt templates
├── utils.py # Helper functions
├── requirements.txt # Python dependencies
├── .env # (Ignored) Secrets
├── credentials.json # (Ignored) Google OAuth Client
├── token.json # (Ignored) Gmail Session
└── logs/ # (Ignored) Application logs

text

---

## 🚀 How to Run It (Setup Guide)

### 1. Prerequisites
- Python 3.11+
- MySQL Server running
- [Ollama](https://ollama.com/download) installed

### 2. Clone the Repository
```bash
git clone https://github.com/engr-ghulammustafaahmed/Python-AI-Agents.git
cd Python-AI-Agents
3. Install Dependencies
bash
pip install -r requirements.txt
4. Pull the AI Model
bash
ollama pull tinyllama
5. Configure MySQL
Create a database (e.g., email_agent_db).

Create a .env file in the root with your credentials:

env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=email_agent_db
SEND_AUTO=False   # Set to True to auto-send, else drafts are created
6. Set up Gmail API
Go to Google Cloud Console.

Enable Gmail API.

Create an OAuth Desktop Client.

Download credentials.json and place it in the project root.

7. Run the Agent
bash
python main.py
The browser will open for OAuth consent (first time only).

The agent will check your Gmail every minute.

🧠 How the Agent Works
Scheduler triggers every minute.

Gmail Reader fetches all unread emails.

LLM (TinyLlama) analyzes the email content.

Agent Logic decides if a reply is needed (ignores spam/promotions).

Reply Generation writes a professional response.

Draft Creation saves it to your Gmail drafts folder.

MySQL Storage saves a record of the interaction for future memory.

🔮 Future Work (Roadmap)
This is an active project. Here are the planned enhancements:

Phase 2: Intelligence Boost
Email Categorization: Automatically label emails as Work, Personal, or Spam before replying.

Priority Scoring: Reply to urgent emails instantly, save low-priority ones for later.

Attachment Summarization: Use AI to summarize PDFs and Word documents attached to emails.

Phase 3: Memory & Context
RAG (Retrieval-Augmented Generation): Implement a Vector Database (Chroma/FAISS) so the AI remembers past conversations with the same sender. No more generic replies—it will know the context!

Phase 4: Multi-Agent System
Agent 1 (Reader): Extracts and cleans email data.

Agent 2 (Classificator): Decides intent.

Agent 3 (Drafting): Generates the reply.

Agent 4 (Reviewer): Checks grammar and tone before sending.

Phase 5: Voice Integration
Add text-to-speech to "read out" new emails.

Voice commands: "Reply to this email", "Archive this", etc.

🤝 Contributing
Pull requests and suggestions are welcome! If you find a bug, please open an issue.

📜 License
This project is open-source and available under the MIT License.

📧 Connect
Author: Ghulam Mustafa Ahmed

GitHub: engr-ghulammustafaahmed

text

---

### 🖥️ Step 3: Run these Git Commands (In Order)

Open your PowerShell/Terminal inside your `Email-agent` folder and run these commands **one by one**.

**Important**: Make sure the `.gitignore` and `README.md` files are saved in the folder before running these.

```powershell
# 1. Initialize Git (if not already done)
git init

# 2. Add the remote origin (skip if already done)
git remote add origin https://github.com/engr-ghulammustafaahmed/Python-AI-Agents.git

# 3. Set your main branch name
git branch -M main

# 4. Add all files EXCEPT the ones ignored (secrets are safe!)
git add .

# 5. Commit the changes with a message
git commit -m "Initial commit: AI Email Agent with TinyLlama and Gmail API"

# 6. Push to GitHub
git push -u origin main
