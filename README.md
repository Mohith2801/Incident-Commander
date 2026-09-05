# 🚨 AI Software Incident Commander

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-LLM-green?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-Live%20AI-purple?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?style=for-the-badge&logo=streamlit)
![RAG](https://img.shields.io/badge/RAG-Knowledge%20Retrieval-yellow?style=for-the-badge)
![HITL](https://img.shields.io/badge/Human--in--the--Loop-Approval-red?style=for-the-badge)
![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)

</p>

<p align="center">
<b>An AI-powered multi-agent incident investigation platform that analyzes application logs, metrics, database events, deployments, and historical knowledge to identify root causes, validate findings, and generate structured incident reports with human-in-the-loop approval.</b>
</p>

---

# 🚀 Live Demo

### 🌐 Streamlit Application

👉 **https://incident-commander-nxajqnrs43zdexjv43y72u.streamlit.app/**

### 💻 GitHub Repository

👉 **https://github.com/Mohith2801/Incident-Commander**

The application is deployed using Streamlit Community Cloud and provides an interactive interface for investigating software incidents.

---

# 📖 Table of Contents

- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Project Goals](#-project-goals)
- [Solution](#-solution)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [High-Level Architecture](#-high-level-architecture)
- [Project Workflow](#-project-workflow)
- [Detailed Workflow](#-detailed-workflow)
- [Multi-Agent Architecture](#-multi-agent-architecture)
- [Agent Responsibilities](#-agent-responsibilities)
- [RAG Knowledge System](#-rag-knowledge-system)
- [Evidence Correlation](#-evidence-correlation)
- [Root Cause Analysis](#-root-cause-analysis)
- [Critic Validation](#-critic-validation)
- [Human-in-the-Loop](#-human-in-the-loop)
- [RCA Rework](#-rca-rework)
- [Final Incident Report](#-final-incident-report)
- [State Management](#-state-management)
- [Data Sources](#-data-sources)
- [Example Investigation](#-example-investigation)
- [Execution Modes](#-execution-modes)
- [Streamlit Application](#-streamlit-application)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Security](#-security)
- [Design Decisions](#-design-decisions)
- [Limitations](#-limitations)
- [Future Enhancements](#-future-enhancements)
- [Project Capabilities](#-project-capabilities)
- [Resume Highlights](#-resume-highlights)
- [Interview Explanation](#-interview-explanation)
- [Author](#-author)
- [Support](#-support)

---

# 📖 Project Overview

The **AI Software Incident Commander** is an AI-assisted software incident investigation platform designed to help engineers analyze incidents by bringing together multiple sources of operational evidence.

When a production application starts failing, the cause is often not visible in a single location.

For example, an HTTP 500 error may actually be caused by:

```text
Recent Deployment
       ↓
Configuration Change
       ↓
Database Connection Pool Problem
       ↓
Database Connection Failures
       ↓
Application Errors
       ↓
HTTP 500 Responses
       ↓
Increased Latency
```

An engineer investigating such an incident may need to inspect logs, metrics, database events, deployment history, and internal troubleshooting documentation.

The Incident Commander automates much of this investigation process through a **stateful multi-agent workflow**.

Instead of relying on one general-purpose agent, the system uses specialized agents for different investigation tasks.

The workflow then combines their findings, correlates the evidence, proposes a root cause, validates that root cause, and pauses for human approval before generating the final report.

---

# 🎯 Problem Statement

Software incidents can generate large amounts of operational data.

During an incident, engineers may have to manually inspect:

- Application logs
- HTTP status codes
- API metrics
- Database events
- Deployment history
- Configuration changes
- Historical incidents
- Runbooks
- Troubleshooting documentation

A traditional investigation can look like:

```text
Incident Detected
       ↓
Check Logs
       ↓
Check Metrics
       ↓
Check Database
       ↓
Check Deployment
       ↓
Search Documentation
       ↓
Correlate Evidence
       ↓
Form Hypothesis
       ↓
Validate Hypothesis
       ↓
Write Incident Report
```

This process can become slow and repetitive, particularly when several systems are involved.

The challenge is therefore not simply:

> "Find the error."

The more important question is:

> "What combination of events most likely caused the incident?"

---

# 🎯 Project Goals

The project is designed around the following goals:

1. Automate repetitive incident investigation tasks.
2. Collect evidence from multiple operational sources.
3. Retrieve relevant historical knowledge.
4. Correlate events across logs, metrics, databases, and deployments.
5. Generate an evidence-based root-cause hypothesis.
6. Assign confidence to the proposed root cause.
7. Independently validate the RCA using a Critic Agent.
8. Keep a human involved before finalizing the investigation.
9. Allow RCA rework when the reviewer is not satisfied.
10. Generate a structured incident report.
11. Provide an offline execution path for reliable demonstrations and testing.
12. Provide a Live AI execution path using Groq.
13. Demonstrate a practical stateful AI workflow using LangGraph.

---

# 💡 Solution

The Incident Commander uses a **multi-agent architecture orchestrated with LangGraph**.

Each specialized agent focuses on one responsibility.

```text
                         INCIDENT
                            │
                            ▼
                    Supervisor Agent
                            │
                            ▼
                      RAG Retrieval
                            │
                            ▼
                    Log Investigation
                            │
                            ▼
                  Metrics Investigation
                            │
                            ▼
                 Database Investigation
                            │
                            ▼
                Deployment Investigation
                            │
                            ▼
                   Event Correlation
                            │
                            ▼
                   Root Cause Analysis
                            │
                            ▼
                     Critic Review
                            │
                            ▼
                     Human Review
                            │
                  ┌─────────┴─────────┐
                  │                   │
               APPROVE              REWORK
                  │                   │
                  ▼                   ▼
             Final Report        Root Cause
                  │               Analysis
                  ▼                   │
                 END             Critic Review
                                      │
                                      ▼
                                 Human Review
```

---

# ✨ Key Features

## 🤖 Multi-Agent Investigation

The investigation is divided into specialized agents rather than placing every responsibility inside one large agent.

---

## 📝 Application Log Analysis

The Log Agent analyzes application logs and identifies relevant errors and patterns.

It can investigate:

- Error messages
- HTTP status codes
- Timestamps
- Database-related errors
- Repeated failures

---

## 📊 Metrics Analysis

The Metrics Agent investigates operational metrics.

It can identify:

- Increased error rates
- Increased latency
- Abnormal API behavior
- Performance degradation

---

## 🗄️ Database Investigation

The Database Agent analyzes database events.

It focuses on:

- Database connection failures
- Connection pool problems
- Resource-related failures
- Database errors

---

## 🚀 Deployment Analysis

The Deployment Agent analyzes deployment history.

It can identify:

- Recent releases
- Version changes
- Deployment timestamps
- Potentially related deployment activity

---

## 📚 Retrieval-Augmented Generation

The system includes a local RAG pipeline for retrieving relevant operational knowledge.

Knowledge can include:

- Historical incidents
- Runbooks
- Troubleshooting documentation

---

## 🔗 Evidence Correlation

The Correlation Agent connects findings from multiple sources.

For example:

```text
Deployment
    ↓
Database Configuration
    ↓
Connection Pool Exhaustion
    ↓
Database Errors
    ↓
HTTP 500 Errors
```

---

## 🧠 Root Cause Analysis

The Root Cause Agent generates:

- Root cause
- Confidence score
- Rationale
- Supporting evidence
- Evidence that should be verified

---

## 🔍 Critic Validation

A dedicated Critic Agent evaluates the proposed RCA before it can proceed.

Possible outcomes include:

```text
PASS
REWORK
```

---

## 👤 Human-in-the-Loop

The workflow pauses before finalization.

A human reviewer can:

- Review the evidence
- Review the RCA
- Review the confidence
- Review the Critic verdict
- Approve the RCA
- Request rework
- Provide feedback

---

## 🔄 RCA Rework

If the human reviewer requests rework, the workflow returns to RCA generation.

```text
Human Feedback
      ↓
Root Cause Agent
      ↓
Updated RCA
      ↓
Critic Agent
      ↓
Human Review
```

---

## 📄 Final Incident Report

Once the RCA is approved, the system generates a structured final incident report.

---

## ⚡ Offline Mode

The project provides an Offline / Demo mode that can execute the investigation without depending on external LLM calls for the demonstration workflow.

---

## 🧠 Live AI Mode

Live AI mode uses the configured Groq LLM for AI-assisted reasoning and final report generation.

---

# 🏗️ System Architecture

The application is divided into several logical layers.

```text
┌───────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                        │
│                                                               │
│                    Streamlit Application                      │
│                                                               │
│ Incident Input | Evidence | RCA | Critic | HITL | Report    │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                        │
│                                                               │
│                         LangGraph                             │
│                                                               │
│ State | Routing | Checkpoints | Interrupts | Rework           │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                         AGENT LAYER                           │
│                                                               │
│ Supervisor | Logs | Metrics | Database | Deployment           │
│ Correlation | Root Cause | Critic | Final Report              │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    DATA / KNOWLEDGE LAYER                      │
│                                                               │
│ Logs | Metrics | Database | Deployments | Knowledge Base       │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                         AI LAYER                              │
│                                                               │
│                    LangChain + Groq                           │
│                                                               │
│                 Live AI Reasoning                             │
└───────────────────────────────────────────────────────────────┘
```

---

# 🏛️ High-Level Architecture

The main components are:

### Presentation Layer

Streamlit provides the user-facing interface.

### Orchestration Layer

LangGraph controls the investigation workflow and maintains state.

### Agent Layer

Specialized agents investigate different evidence sources.

### Knowledge Layer

Local datasets and documentation provide operational evidence and historical context.

### AI Layer

Groq provides LLM-powered reasoning in Live AI mode.

---

# 🔄 Project Workflow

The main LangGraph workflow is:

```text
START
  │
  ▼
Supervisor
  │
  ▼
RAG
  │
  ▼
Logs
  │
  ▼
Metrics
  │
  ▼
Database
  │
  ▼
Deployment
  │
  ▼
Correlation
  │
  ▼
Root Cause
  │
  ▼
Critic
  │
  ▼
Human Review
  │
  ├───────────────┐
  │               │
Approve          Rework
  │               │
  ▼               ▼
Report       Human Rework
  │               │
  │               ▼
  │          Root Cause
  │               │
  │               ▼
  │             Critic
  │               │
  │               ▼
  │         Human Review
  │
  ▼
 END
```

The graph is stateful and supports conditional routing.

---

# 🔍 Detailed Workflow

## 1. Incident Initialization

The application begins with incident information such as:

```text
Incident ID
Service
Severity
Description
```

This information is placed into the shared incident state.

---

## 2. Supervisor Agent

The Supervisor initializes the investigation and provides the entry point into the workflow.

It coordinates the investigation sequence.

---

## 3. RAG Retrieval

The system searches the local knowledge base for relevant historical information.

Relevant documentation is added to the investigation context.

---

## 4. Log Investigation

The Log Agent searches application logs.

The goal is to identify:

```text
Errors
HTTP 500 responses
Database errors
Repeated failures
Relevant timestamps
```

---

## 5. Metrics Investigation

The Metrics Agent analyzes API metrics.

It looks for:

```text
Error-rate increases
Latency increases
Performance degradation
Abnormal request behavior
```

---

## 6. Database Investigation

The Database Agent investigates database events.

It looks for:

```text
Connection failures
Pool exhaustion
Database errors
Resource problems
```

---

## 7. Deployment Investigation

The Deployment Agent checks deployment history.

It looks for:

```text
Recent releases
Version changes
Deployment timestamps
Potential configuration changes
```

---

## 8. Correlation

The Correlation Agent combines the evidence.

For example:

```text
Deployment v2.4.1
        ↓
Database Pool Configuration
        ↓
Pool Exhaustion
        ↓
Database Connection Errors
        ↓
HTTP 500 Responses
```

---

## 9. Root Cause Analysis

The Root Cause Agent evaluates the evidence and proposes the most likely cause.

The result includes a confidence score.

---

## 10. Critic Review

The Critic Agent independently reviews the proposed RCA.

It checks whether the conclusion is sufficiently supported by the collected evidence.

---

## 11. Human Review

The workflow pauses.

The reviewer can choose:

```text
Approve
```

or:

```text
Request Rework
```

---

## 12. RCA Rework

If rework is requested, reviewer feedback is passed back into the investigation.

The Root Cause Agent generates an updated RCA.

The updated RCA is then reviewed again.

---

## 13. Final Report

After approval, the Final Report Agent produces the structured incident report.

---

# 🤖 Multi-Agent Architecture

The project uses specialized agents instead of one monolithic AI agent.

| Agent | Responsibility |
|---|---|
| Supervisor Agent | Coordinates the investigation |
| Log Agent | Investigates application logs |
| Metrics Agent | Investigates performance metrics |
| Database Agent | Investigates database events |
| Deployment Agent | Investigates deployment history |
| Correlation Agent | Connects evidence across sources |
| Root Cause Agent | Generates the RCA |
| Critic Agent | Validates the RCA |
| Final Report Agent | Generates the final report |

This architecture provides clear separation of responsibilities.

---

# 🧭 Agent Responsibilities

## Supervisor Agent

Responsible for:

- Investigation initialization
- Workflow coordination
- Investigation sequencing

---

## Log Agent

Responsible for:

- Application log analysis
- Error identification
- HTTP failure identification
- Database-related error identification

---

## Metrics Agent

Responsible for:

- API metric analysis
- Error-rate analysis
- Latency analysis
- Performance degradation detection

---

## Database Agent

Responsible for:

- Database event analysis
- Connection failure detection
- Pool exhaustion detection
- Database-related evidence

---

## Deployment Agent

Responsible for:

- Deployment history
- Release identification
- Version analysis
- Deployment timing

---

## Correlation Agent

Responsible for:

- Temporal correlation
- Cross-source evidence analysis
- Connecting related events
- Building an evidence chain

---

## Root Cause Agent

Responsible for:

- RCA generation
- Confidence scoring
- Evidence-based reasoning
- RCA rationale

---

## Critic Agent

Responsible for:

- RCA validation
- Evidence consistency
- Detecting unsupported conclusions
- Returning PASS or REWORK

---

## Final Report Agent

Responsible for:

- Final report generation
- Incident summary
- RCA presentation
- Evidence summary
- Investigation completion

---

# 📚 RAG Knowledge System

The project includes a lightweight Retrieval-Augmented Generation system.

The knowledge base contains operational documentation.

```text
knowledge/
│
├── incidents/
│   └── INC-0001.md
│
├── runbooks/
│   └── database_connection_pool.md
│
└── troubleshooting/
    └── http_500_database_errors.md
```

---

# 🔎 RAG Workflow

```text
Incident
    │
    ▼
Create Retrieval Context
    │
    ▼
Search Knowledge Base
    │
    ├── Historical Incidents
    ├── Runbooks
    └── Troubleshooting Guides
    │
    ▼
Relevant Documents
    │
    ▼
Investigation Context
```

The current implementation uses an in-memory vector store and local embeddings.

This keeps the demonstration self-contained without requiring an external vector database.

---

# 🔗 Evidence Correlation

One of the most important parts of the project is evidence correlation.

Individual findings may not explain the incident by themselves.

For example:

```text
Finding 1:
HTTP 500 errors increased.

Finding 2:
Database connection failures increased.

Finding 3:
Connection pool exhaustion was detected.

Finding 4:
A recent deployment was identified.
```

The correlation agent combines these findings:

```text
Recent Deployment
       ↓
Database Pool Problem
       ↓
Pool Exhaustion
       ↓
Database Connection Failures
       ↓
HTTP 500 Errors
```

This provides a stronger basis for RCA than looking at individual errors independently.

---

# 🧠 Root Cause Analysis

The Root Cause Agent produces an evidence-based hypothesis.

Its output includes:

```text
Root Cause
Confidence
Rationale
Supporting Evidence
Evidence to Verify
```

Example:

```text
Root Cause:

Database connection pool misconfiguration introduced
in deployment v2.4.1, leading to connection pool exhaustion
and subsequent HTTP 500 errors.

Confidence:

95%
```

The RCA is then passed to the Critic Agent.

---

# 🔍 Critic Validation

The Critic Agent acts as an independent verification layer.

The purpose is to prevent the system from blindly accepting the first RCA.

```text
Root Cause
    │
    ▼
Critic Agent
    │
    ├── PASS
    │
    └── REWORK
```

A PASS allows the investigation to continue to human review.

A REWORK result allows the RCA to be reconsidered.

---

# 👤 Human-in-the-Loop

Human review is an important part of the architecture.

The system intentionally pauses before generating the final report.

```text
AI Investigation
       ↓
Root Cause
       ↓
Critic
       ↓
Human Review
       ↓
┌──────┴──────┐
│             │
Approve       Rework
│             │
▼             ▼
Report       RCA
```

This provides a human validation layer between AI reasoning and final incident documentation.

---

# 🔄 RCA Rework

If the reviewer disagrees with the RCA, the reviewer can request rework.

The workflow becomes:

```text
Human Review
      ↓
Reviewer Feedback
      ↓
Root Cause Agent
      ↓
Updated RCA
      ↓
Critic Agent
      ↓
Human Review
```

This iterative workflow is implemented using LangGraph state transitions.

---

# 📄 Final Incident Report

Once the RCA is approved, the Final Report Agent creates a structured report.

The report contains:

```text
Incident ID
Service
Severity
Description
Root Cause
Confidence
Root Cause Rationale
Correlations
Investigation Findings
Evidence to Verify
Generated Timestamp
```

Example:

```text
==================================================

INCIDENT FINAL REPORT

Incident ID: INC-0001
Service: Example Service
Severity: High

==================================================

ROOT CAUSE

Database connection pool misconfiguration introduced
in deployment v2.4.1, leading to connection pool exhaustion
and subsequent HTTP 500 errors.

Confidence: 95%

==================================================

ROOT CAUSE RATIONALE

The deployment changed database connection-pool
configuration. The pool subsequently became exhausted,
resulting in database connection failures and HTTP 500
responses.

==================================================

CORRELATIONS

Deployment
    ↓
Database Pool Configuration
    ↓
Pool Exhaustion
    ↓
Database Errors
    ↓
HTTP 500

==================================================

END OF INCIDENT REPORT
```

---

# 🧠 State Management

The investigation uses a shared state object.

The state contains information such as:

```text
Incident Information
        │
        ├── Incident ID
        ├── Service
        ├── Severity
        └── Description
        │
        ▼
Evidence
        │
        ├── Logs
        ├── Metrics
        ├── Database
        └── Deployment
        │
        ▼
RAG Results
        │
        ▼
Investigation Findings
        │
        ▼
Correlations
        │
        ▼
Root Cause
        │
        ├── Confidence
        └── Rationale
        │
        ▼
Critic Review
        │
        └── Verdict
        │
        ▼
Human Review
        │
        ├── Approval
        └── Feedback
        │
        ▼
Final Result
```

LangGraph checkpointing is used to maintain workflow state around the human review stage.

---

# 💾 Data Sources

The project uses local operational datasets.

## Application Logs

```text
data/logs/application_logs.csv
```

Contains application log events used during investigation.

---

## API Metrics

```text
data/metrics/api_metrics.csv
```

Contains API and performance metrics.

---

## Database Events

```text
data/databases/database_events.csv
```

Contains database-related events.

---

## Deployment History

```text
data/deployments/deployment_history.csv
```

Contains deployment information and release history.

---

# 🔬 Example Investigation

The included sample incident demonstrates a database-related application failure.

The application experiences:

```text
HTTP 500 Errors
Database Errors
Connection Pool Problems
Increased Latency
Recent Deployment
```

The investigation connects these signals.

---

# 🔗 Example Evidence Chain

```text
                 Deployment v2.4.1
                         │
                         ▼
              Database Configuration
                         │
                         ▼
               Connection Pool Issue
                         │
                         ▼
                Pool Exhaustion
                         │
                         ▼
              Database Connection Errors
                         │
                         ▼
                   HTTP 500 Errors
                         │
                         ▼
                  Latency Increase
```

This evidence chain provides the foundation for the proposed RCA.

---

# 🎯 Example RCA Result

The demonstrated workflow can produce a root cause similar to:

```text
Database connection pool misconfiguration introduced
in deployment v2.4.1, leading to connection pool exhaustion
and subsequent HTTP 500 errors.
```

The demonstrated RCA confidence was:

```text
95%
```

The Critic Agent also produced:

```text
PASS
```

The investigation then reached the Human Review stage.

---

# ⚡ Execution Modes

The application supports two execution modes.

---

## 🟢 Offline / Demo

Offline mode is designed for:

- Demonstrations
- Local testing
- Reproducible execution
- Environments without an LLM
- External API quota limitations

The offline workflow uses deterministic logic to demonstrate the investigation pipeline.

---

## 🟣 Live AI

Live AI mode uses the configured Groq model.

The architecture becomes:

```text
Incident
   ↓
Evidence
   ↓
RAG
   ↓
Agent Reasoning
   ↓
Correlation
   ↓
RCA
   ↓
Critic
   ↓
Human Review
   ↓
Final Report
```

The Final Report Agent also supports deterministic fallback behavior if Live AI report generation is unavailable.

---

# 🖥️ Streamlit Application

The project provides a Streamlit web interface.

The UI provides:

## Execution Mode Selection

```text
Offline / Demo
Live AI
```

---

## Incident Investigation

The user can start an investigation and observe the workflow.

---

## Evidence Display

The interface can present findings from:

- Logs
- Metrics
- Database
- Deployment
- RAG

---

## Root Cause Display

The interface presents:

- Root cause
- Confidence
- Rationale
- Supporting evidence

---

## Critic Review

The interface displays the Critic Agent's verdict.

---

## Human Review

The interface allows the reviewer to:

```text
Approve RCA
```

or:

```text
Request RCA Rework
```

---

## Final Report

Once approved, the final report is displayed and can be downloaded.

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application language |
| LangGraph | Stateful multi-agent orchestration |
| LangChain | LLM and AI application framework |
| Groq | Live AI inference |
| Streamlit | Web interface |
| Pandas | Dataset processing |
| Scikit-learn | Local embedding support |
| Python-dotenv | Environment configuration |
| Git | Version control |
| GitHub | Source repository |
| Streamlit Community Cloud | Deployment |

---

# 📂 Project Structure

```text
Incident-Commander/
│
├── agents/
│   ├── __init__.py
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
│   ├── __init__.py
│   ├── config.py
│   ├── llm.py
│   ├── graph.py
│   └── rag.py
│
├── data/
│   ├── databases/
│   │   └── database_events.csv
│   │
│   ├── deployments/
│   │   └── deployment_history.csv
│   │
│   ├── logs/
│   │   └── application_logs.csv
│   │
│   └── metrics/
│       └── api_metrics.csv
│
├── knowledge/
│   ├── incidents/
│   │   └── INC-0001.md
│   │
│   ├── runbooks/
│   │   └── database_connection_pool.md
│   │
│   └── troubleshooting/
│       └── http_500_database_errors.md
│
├── tools/
│   ├── __init__.py
│   ├── log_tools.py
│   ├── metrics_tools.py
│   ├── database_tools.py
│   └── deployment_tools.py
│
├── ui/
│   └── streamlit_app.py
│
├── tests/
│   └── ...
│
├── test_graph.py
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Configuration

The application uses environment variables for configuration.

A template is provided in:

```text
.env.example
```

Create a local:

```text
.env
```

file when running the project locally.

---

# 🔐 Environment Variables

Example configuration:

```env
APP_ENV=development
LOG_LEVEL=INFO

LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b

GROQ_API_KEY=your_groq_api_key_here

MAX_EVIDENCE_ITEMS=20
CONFIDENCE_THRESHOLD=0.70

DATA_DIR=data
INCIDENTS_DIR=data/incidents
LOGS_DIR=data/logs
METRICS_DIR=data/metrics
DEPLOYMENTS_DIR=data/deployments
DATABASES_DIR=data/databases
```

---

# 📥 Installation

## Prerequisites

Install:

- Python 3.12+
- Git
- pip

A Groq API key is required only for Live AI functionality.

---

# 📦 Clone the Repository

```bash
git clone https://github.com/Mohith2801/Incident-Commander.git
```

Move into the project:

```bash
cd Incident-Commander
```

---

# 🐍 Create a Virtual Environment

## Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

---

## Linux / macOS

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

---

# 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Configure Groq

Create a `.env` file.

Add:

```env
GROQ_API_KEY=your_groq_api_key_here
```

You can use Offline / Demo mode without configuring a Groq API key.

---

# ▶️ Running the Application

Start Streamlit:

```bash
streamlit run ui/streamlit_app.py
```

Streamlit will provide a local URL.

Open the URL in a browser.

---

# 🧪 Testing

The project includes an integration test for the investigation workflow.

Run:

```bash
python test_graph.py
```

Offline execution can be used to test the workflow without repeatedly consuming external LLM usage.

---

# 🔬 RAG Testing

The RAG module can be executed independently.

Use:

```bash
python -m app.rag
```

This tests retrieval against the local knowledge base.

---

# ☁️ Deployment

The project is deployed through Streamlit Community Cloud.

## Repository

```text
https://github.com/Mohith2801/Incident-Commander
```

## Main Branch

```text
main
```

## Streamlit Entry Point

```text
ui/streamlit_app.py
```

## Live Application

```text
https://incident-commander-nxajqnrs43zdexjv43y72u.streamlit.app/
```

---

# 🔐 Deployment Secrets

Sensitive credentials should not be committed to GitHub.

For Streamlit deployment, secrets can be configured through Streamlit's secret management system.

Example:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Never place a real API key directly in the source code.

---

# 🔒 Security

The repository excludes sensitive local configuration.

Examples include:

```text
.env
.env.*
.streamlit/secrets.toml
.venv/
__pycache__/
*.pyc
```

The project uses environment variables and deployment secrets for sensitive configuration.

---

# 🧩 Design Decisions

## Why Multi-Agent Architecture?

Incident investigation involves several distinct responsibilities.

Separating them makes the system:

- Easier to understand
- Easier to test
- Easier to debug
- Easier to extend

---

## Why LangGraph?

LangGraph is particularly useful because the workflow is not simply:

```text
Input → Output
```

The investigation contains:

```text
State
Routing
Conditional Decisions
Human Interrupts
Rework
Checkpointing
```

LangGraph provides the orchestration capabilities needed for this workflow.

---

## Why RAG?

Historical incidents and operational documentation can contain useful information about previously observed failures.

RAG allows the investigation to retrieve relevant context from the knowledge base.

---

## Why a Critic Agent?

An AI-generated RCA should not automatically be treated as correct.

The Critic Agent provides a second validation layer.

```text
RCA
 ↓
Critic
 ↓
PASS / REWORK
```

---

## Why Human-in-the-Loop?

Incident investigations can have operational consequences.

Human review allows an engineer to validate the RCA before the system generates the final incident report.

---

## Why Offline Mode?

External AI services can have:

- Usage limits
- Availability issues
- Network dependencies
- Rate limits

Offline mode provides a deterministic path for testing and demonstrations.

---

# 🧠 Engineering Architecture Principles

The project follows several engineering principles.

### Separation of Concerns

Each component has a specific responsibility.

### Stateful Processing

Investigation information is maintained through shared state.

### Evidence-Based Reasoning

The RCA is derived from collected operational evidence.

### Independent Validation

The Critic Agent reviews the proposed RCA.

### Human Oversight

The final investigation decision remains subject to human review.

### Graceful Degradation

The system can operate in Offline / Demo mode.

### Extensibility

New agents and integrations can be added without redesigning the entire workflow.

---

# ⚠️ Limitations

The current implementation is a portfolio and demonstration-oriented incident investigation platform.

It currently has several limitations.

### Local Data

The operational datasets are local/sample data rather than direct production telemetry.

### Local Knowledge Base

The RAG system currently uses a local knowledge base.

### No Production Observability Integration

The system does not currently connect directly to systems such as production monitoring platforms.

### No Automatic Remediation

The system identifies and reports potential causes but does not automatically modify production infrastructure.

### External LLM Dependency

Live AI functionality depends on the availability and limits of the configured Groq service.

### AI Validation

AI-generated conclusions should be reviewed by qualified engineers before being used for real production decisions.

---

# 🚀 Future Enhancements

The architecture can be extended significantly.

## 📡 Real-Time Log Integration

Integrate directly with production logging systems.

Possible integrations:

- Elasticsearch
- OpenSearch
- Loki
- Cloud logging platforms

---

## 📊 Real-Time Metrics

Integrate with:

- Prometheus
- Grafana
- Cloud monitoring systems

---

## ☸️ Kubernetes Investigation

Add agents capable of analyzing:

- Pods
- Deployments
- Services
- Kubernetes events
- Container restarts
- Resource usage

---

## ☁️ Cloud Integration

Add integrations for:

- AWS
- Microsoft Azure
- Google Cloud

---

## 💬 Notification Systems

Automatically send incident summaries to:

- Slack
- Microsoft Teams
- Email

---

## 🎫 Incident Management

Integrate with:

- Jira
- ServiceNow
- PagerDuty

---

## 🤖 Automated Remediation

Future versions could recommend or execute controlled remediation actions.

Example:

```text
Incident
   ↓
Root Cause
   ↓
Recommended Fix
   ↓
Human Approval
   ↓
Controlled Remediation
   ↓
Verification
```

---

## 🗃️ Persistent Incident Database

Store completed investigations and RCA history.

This would allow the system to learn from previous incidents.

---

## 🔎 Production-Grade RAG

The local vector store could eventually be replaced with:

- PostgreSQL + pgvector
- Qdrant
- Pinecone
- Weaviate

---

## 🔐 Authentication and Authorization

Add:

- User authentication
- Role-based access
- Engineer permissions
- Reviewer permissions
- Administrator permissions

---

## 📊 Incident Analytics

Add dashboards showing:

```text
Incident Frequency
Most Affected Services
Common Root Causes
RCA Confidence
Incident Severity
Investigation Duration
```

---

# 📈 Project Capabilities

| Capability | Status |
|---|---|
| Python Application | ✅ |
| Multi-Agent Architecture | ✅ |
| LangGraph Workflow | ✅ |
| Stateful Investigation | ✅ |
| Supervisor Agent | ✅ |
| Log Investigation | ✅ |
| Metrics Investigation | ✅ |
| Database Investigation | ✅ |
| Deployment Investigation | ✅ |
| RAG Knowledge Retrieval | ✅ |
| Evidence Correlation | ✅ |
| Root Cause Analysis | ✅ |
| Confidence Scoring | ✅ |
| Critic Validation | ✅ |
| Human-in-the-Loop | ✅ |
| RCA Rework | ✅ |
| Final Incident Report | ✅ |
| Offline / Demo Mode | ✅ |
| Live AI Mode | ✅ |
| Streamlit Interface | ✅ |
| GitHub Repository | ✅ |
| Cloud Deployment | ✅ |

---

# 📊 End-to-End Architecture Summary

The complete system can be summarized as:

```text
                         ┌───────────────┐
                         │    User       │
                         └───────┬───────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │   Streamlit UI   │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │    LangGraph     │
                       │   Orchestrator   │
                       └────────┬─────────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
           Logs              Metrics           Database
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
                          Deployment
                                │
                                ▼
                              RAG
                                │
                                ▼
                          Correlation
                                │
                                ▼
                          Root Cause
                                │
                                ▼
                             Critic
                                │
                                ▼
                         Human Review
                                │
                     ┌──────────┴──────────┐
                     │                     │
                  APPROVE                REWORK
                     │                     │
                     ▼                     ▼
               Final Report          Root Cause
                     │
                     ▼
                    END
```

---

# 💼 Resume Highlights

This project demonstrates practical experience in:

- Python
- Artificial Intelligence
- Generative AI
- Multi-Agent Systems
- LangGraph
- LangChain
- Groq
- Retrieval-Augmented Generation
- LLM Integration
- Stateful AI Workflows
- Root Cause Analysis
- Event Correlation
- Human-in-the-Loop Systems
- Streamlit
- Data Processing
- Software Architecture
- DevOps Concepts
- Incident Management

---

# 📝 Resume Project Description

### AI Software Incident Commander

> Developed an AI-powered multi-agent incident investigation platform using Python, LangGraph, LangChain, Groq, RAG, and Streamlit. Built specialized agents for log, metrics, database, deployment, correlation, root-cause analysis, critic validation, and incident reporting. Implemented stateful human-in-the-loop workflows with RCA rework and approval, along with Offline and Live AI execution modes. Deployed the application using Streamlit Community Cloud.

---

# 🎤 Interview Explanation

A concise explanation for interviews:

> "I built an AI Software Incident Commander that automates software incident investigation using a multi-agent architecture. The workflow is orchestrated using LangGraph. Different agents investigate application logs, metrics, database events, and deployment history. I also implemented RAG so the system can retrieve relevant historical incidents and troubleshooting documentation. After collecting the evidence, a Correlation Agent connects the different signals and the Root Cause Agent generates an RCA with a confidence score. A separate Critic Agent validates the RCA. Before generating the final report, the LangGraph workflow pauses for human review. The reviewer can either approve the RCA or request rework, which sends the workflow back to root-cause analysis. I also implemented Offline and Live AI modes and deployed the application using Streamlit Community Cloud."

---

# ⭐ Why This Project Is Different

This project goes beyond a basic chatbot.

It demonstrates an end-to-end AI engineering system:

```text
Data Collection
      ↓
Knowledge Retrieval
      ↓
Multi-Agent Investigation
      ↓
Evidence Correlation
      ↓
Root Cause Analysis
      ↓
AI Validation
      ↓
Human Review
      ↓
Iterative Rework
      ↓
Final Incident Report
```

The project combines:

```text
Multi-Agent AI
+
RAG
+
LangGraph
+
State Management
+
Evidence Correlation
+
Critic Validation
+
Human-in-the-Loop
+
Streamlit
+
Cloud Deployment
```

This makes the project representative of a practical AI-assisted DevOps workflow rather than a simple question-answering application.

---

# 🌐 Project Links

### 🚀 Live Demo

https://incident-commander-nxajqnrs43zdexjv43y72u.streamlit.app/

### 💻 GitHub

https://github.com/Mohith2801/Incident-Commander

---

# 👨‍💻 Author

## Narra Mohith Charan

GitHub:

https://github.com/Mohith2801

---

# ⭐ Support

If you find this project useful or interesting, consider giving the GitHub repository a ⭐ Star.

Feedback, suggestions, and contributions are welcome.

---

# 📄 Disclaimer

This project is intended for educational, portfolio, and demonstration purposes.

The AI-generated root causes and recommendations should not be treated as authoritative production diagnoses without appropriate engineering validation.

For real production incident response, the output should be reviewed by qualified engineers and verified against trusted observability and infrastructure data.

---

# 🚀 Final Summary

The **AI Software Incident Commander** demonstrates how modern AI engineering techniques can be combined with software incident management.

The complete workflow is:

```text
             SOFTWARE INCIDENT
                     │
                     ▼
             ┌───────────────┐
             │   Supervisor  │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │      RAG      │
             └───────┬───────┘
                     │
                     ▼
       ┌─────────────────────────────┐
       │      Evidence Collection    │
       │                             │
       │ Logs | Metrics | DB | Deploy│
       └──────────────┬──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │ Correlation   │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Root Cause   │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │    Critic    │
              └──────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │ Human Review  │
             └───────┬───────┘
                     │
              ┌──────┴──────┐
              │             │
           APPROVE        REWORK
              │             │
              ▼             ▼
       ┌────────────┐   Root Cause
       │Final Report│      │
       └──────┬─────┘      │
              │             │
              ▼             └──► Critic
             END
```

**AI Software Incident Commander** provides a complete foundation for AI-assisted incident investigation and demonstrates the practical use of multi-agent orchestration, RAG, stateful workflows, evidence correlation, critic validation, human oversight, and automated reporting.
