# 🚨 AI Software Incident Commander

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-LLM-green?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-Live%20AI-purple?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?style=for-the-badge&logo=streamlit)
![RAG](https://img.shields.io/badge/RAG-Knowledge%20Retrieval-yellow?style=for-the-badge)
![HITL](https://img.shields.io/badge/Human--in--the--Loop-Approval-red?style=for-the-badge)

</p>

<p align="center">
<b>AI-powered multi-agent incident investigation system for analyzing logs, metrics, database events, deployments, and historical knowledge to identify software incident root causes.</b>
</p>

---

## 🌐 Live Demo

**Try the application:**  
https://incident-commander-nxajqnrs43zdexjv43y72u.streamlit.app/

**GitHub Repository:**  
https://github.com/Mohith2801/Incident-Commander

---

## 📌 Overview

**AI Software Incident Commander** is a multi-agent AI system designed to assist engineers during software incident investigations.

Instead of manually analyzing different sources of operational data, the system coordinates specialized agents that investigate:

- Application logs
- API metrics
- Database events
- Deployment history
- Historical incidents
- Troubleshooting documentation

The collected evidence is then correlated to identify relationships between events and generate an evidence-based **Root Cause Analysis (RCA)**.

A **Critic Agent** validates the proposed RCA, while a **Human-in-the-Loop** review step allows an engineer to approve the conclusion or request rework before the final incident report is generated.

---

## 🎯 Problem Statement

During a software incident, the root cause is often distributed across multiple systems.

For example:

```text
Recent Deployment
       ↓
Database Configuration Change
       ↓
Connection Pool Exhaustion
       ↓
Database Errors
       ↓
HTTP 500 Errors
       ↓
Increased Latency
```

Finding this relationship manually can be time-consuming.

This project provides an automated investigation workflow that combines these signals and presents the engineer with a structured RCA.

---

## ✨ Key Features

- 🤖 **Multi-Agent Investigation** — Specialized agents for different investigation tasks.
- 📊 **Log & Metrics Analysis** — Identifies errors, HTTP failures, latency, and abnormal patterns.
- 🗄️ **Database Investigation** — Analyzes database-related events and connection failures.
- 🚀 **Deployment Analysis** — Correlates incidents with recent deployments.
- 📚 **RAG Knowledge Retrieval** — Retrieves relevant historical incidents and troubleshooting documents.
- 🔗 **Evidence Correlation** — Connects related events across multiple data sources.
- 🧠 **Root Cause Analysis** — Generates RCA with confidence and supporting rationale.
- 🔍 **Critic Validation** — Independently reviews the generated RCA.
- 👤 **Human-in-the-Loop** — Allows engineers to approve or request RCA rework.
- 🔄 **Rework Workflow** — Sends rejected RCAs back for another investigation cycle.
- 📄 **Final Incident Report** — Generates a structured incident report after approval.
- ⚡ **Offline / Demo Mode** — Supports deterministic execution without requiring LLM calls.
- 🧠 **Live AI Mode** — Uses Groq for AI-powered reasoning.
- 🖥️ **Streamlit UI** — Interactive interface for the complete investigation workflow.

---

## 🏗️ Architecture

```text
                    ┌─────────────────┐
                    │  Streamlit UI   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    LangGraph    │
                    │   Orchestrator  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Supervisor Agent│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
            Logs          Metrics        Database
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                       Deployment
                             │
                             ▼
                      RAG Retrieval
                             │
                             ▼
                     Correlation Agent
                             │
                             ▼
                     Root Cause Agent
                             │
                             ▼
                       Critic Agent
                             │
                             ▼
                      Human Review
                       ┌─────┴─────┐
                       ▼           ▼
                    Approve      Rework
                       │           │
                       ▼           └──► RCA
                  Final Report
                       │
                       ▼
                      END
```

---

## 🔄 Workflow

The investigation follows a stateful LangGraph workflow:

```text
START
  ↓
Supervisor
  ↓
RAG Retrieval
  ↓
Log Analysis
  ↓
Metrics Analysis
  ↓
Database Analysis
  ↓
Deployment Analysis
  ↓
Evidence Correlation
  ↓
Root Cause Analysis
  ↓
Critic Review
  ↓
Human Review
  ├── Approve → Final Report → END
  │
  └── Rework → Root Cause → Critic → Human Review
```

This allows the system to perform investigation, validation, and human-guided iteration within a single workflow.

---

## 🤖 Multi-Agent System

| Agent | Responsibility |
|---|---|
| **Supervisor Agent** | Initializes and coordinates the investigation |
| **Log Agent** | Analyzes application logs and errors |
| **Metrics Agent** | Investigates API performance and error metrics |
| **Database Agent** | Analyzes database events and connection failures |
| **Deployment Agent** | Investigates recent deployments |
| **Correlation Agent** | Connects evidence across sources |
| **Root Cause Agent** | Generates the most likely RCA |
| **Critic Agent** | Validates the RCA |
| **Final Report Agent** | Generates the final incident report |

---

## 📚 RAG Knowledge Base

The project includes a local knowledge base containing:

```text
knowledge/
├── incidents/
│   └── INC-0001.md
│
├── runbooks/
│   └── database_connection_pool.md
│
└── troubleshooting/
    └── http_500_database_errors.md
```

The RAG pipeline retrieves relevant documentation and provides additional context to the investigation.

The current implementation uses an **in-memory vector store with local embeddings**, keeping the system lightweight and easy to run.

---

## 👤 Human-in-the-Loop

Before the final report is generated, the workflow pauses for human review.

The reviewer can:

```text
Approve RCA
     │
     ▼
Final Incident Report
```

or:

```text
Request Rework
     │
     ▼
Root Cause Agent
     │
     ▼
Critic Agent
     │
     ▼
Human Review
```

This prevents the system from treating an AI-generated RCA as automatically correct.

---

## 📊 Example Investigation

A sample incident demonstrates a relationship between a recent deployment, database connection pool problems, and HTTP 500 errors.

The resulting RCA can identify:

```text
Database connection pool misconfiguration introduced
in deployment v2.4.1, leading to connection pool exhaustion
and subsequent HTTP 500 errors.
```

The demonstrated workflow produced a **95% RCA confidence** and a **PASS** verdict from the Critic Agent before reaching Human Review.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core development |
| **LangGraph** | Stateful workflow orchestration |
| **LangChain** | LLM application framework |
| **Groq** | Live AI inference |
| **Streamlit** | Web interface |
| **Pandas** | Dataset processing |
| **Scikit-learn** | Local embeddings |
| **Python-dotenv** | Environment configuration |
| **Git & GitHub** | Version control |
| **Streamlit Community Cloud** | Deployment |

---

## 📂 Project Structure

```text
Incident-Commander/
│
├── agents/
│   ├── state.py
│   ├── supervisor_agent.py
│   ├── log_agent.py
│   ├── metrics_agent.py
│   ├── database_agent.py
│   ├── deployment_agent.py
│   ├── correlation_agent.py
│   ├── root_cause_agent.py
│   ├── critic_agent.py
│   └── final_report_agent.py
│
├── app/
│   ├── config.py
│   ├── llm.py
│   ├── graph.py
│   └── rag.py
│
├── data/
│   ├── logs/
│   ├── metrics/
│   ├── databases/
│   └── deployments/
│
├── knowledge/
│   ├── incidents/
│   ├── runbooks/
│   └── troubleshooting/
│
├── tools/
│   ├── log_tools.py
│   ├── metrics_tools.py
│   ├── database_tools.py
│   └── deployment_tools.py
│
├── ui/
│   └── streamlit_app.py
│
├── tests/
│
├── test_graph.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Mohith2801/Incident-Commander.git
cd Incident-Commander
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate environment

**Windows:**

```powershell
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment

Create a `.env` file:

```env
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=your_groq_api_key_here
```

For Offline / Demo mode, a Groq API key is not required.

---

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run ui/streamlit_app.py
```

Then open the local Streamlit URL shown in the terminal.

---

## 🧪 Testing

Run the graph integration test:

```bash
python test_graph.py
```

Run the RAG module independently:

```bash
python -m app.rag
```

Offline mode can be used for reproducible testing without repeatedly calling the external LLM.

---

## 🚀 Future Improvements

- Real-time integration with monitoring and logging platforms
- Prometheus/Grafana integration
- Kubernetes investigation agents
- AWS/Azure/GCP integrations
- Slack and Microsoft Teams notifications
- Jira / ServiceNow incident creation
- Persistent incident history
- Production-grade vector database
- Automated remediation with human approval
- Authentication and role-based access
- Incident analytics dashboard

---

## 📌 Project Highlights

This project demonstrates practical implementation of:

- Multi-Agent AI
- Generative AI
- LangGraph
- LangChain
- Retrieval-Augmented Generation
- Root Cause Analysis
- Evidence Correlation
- Stateful AI Workflows
- Human-in-the-Loop Systems
- Streamlit Application Development
- Cloud Deployment

---

## 👨‍💻 Author

**Narra Mohith Charan**

GitHub:  
https://github.com/Mohith2801/Incident-Commander

---

## ⭐ Support

If you found this project useful, consider giving the repository a ⭐ on GitHub.

---

## ⚠️ Disclaimer

This project is intended for educational, portfolio, and demonstration purposes.

AI-generated incident analysis should be reviewed and verified by qualified engineers before being used for real production incident decisions.
