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
<b>An AI-powered multi-agent incident investigation platform that analyzes logs, metrics, database events, deployments, and historical knowledge to identify root causes, validate findings, and generate incident reports with human-in-the-loop approval.</b>
</p>

---

# 🚀 Live Demo

## 🌐 Streamlit Application

👉 **https://incident-commander-nxajqnrs43zdexjv43y72u.streamlit.app/**

## 💻 GitHub Repository

👉 **https://github.com/Mohith2801/Incident-Commander**

The deployed application provides two execution modes:

- ⚡ **Offline / Demo Mode** — Runs the investigation workflow without external LLM calls.
- 🧠 **Live AI Mode** — Uses Groq-powered LLM reasoning for AI-assisted investigation and report generation.

---

# 📖 Project Overview

The **AI Software Incident Commander** is an AI-assisted incident investigation system designed to help engineers analyze software failures and identify their most likely root causes.

During a production incident, engineers typically need to inspect multiple sources of operational information:

- Application logs
- API metrics
- Database events
- Deployment history
- Historical incidents
- Troubleshooting documentation
- Operational runbooks

Manually analyzing and correlating these sources can be time-consuming and can result in important relationships being missed.

This project automates the investigation process using a **stateful multi-agent workflow built with LangGraph**.

The system:

```text
Incident
   ↓
Collect Operational Evidence
   ↓
Retrieve Relevant Knowledge
   ↓
Analyze Logs
   ↓
Analyze Metrics
   ↓
Analyze Database Events
   ↓
Analyze Deployments
   ↓
Correlate Evidence
   ↓
Generate Root Cause
   ↓
Critic Verification
   ↓
Human Review
   ↓
Final Incident Report
