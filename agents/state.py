from __future__ import annotations

from typing import Any, TypedDict


class AegisIncidentState(TypedDict, total=False):
    # ============================================================
    # INCIDENT INFORMATION
    # ============================================================
    incident_id: str
    description: str
    severity: str
    service: str

    # ============================================================
    # EXECUTION MODE
    # ============================================================
    # Possible values:
    # - "live"    -> Uses the configured Groq LLM
    # - "offline" -> Deterministic demo mode with no LLM calls
    execution_mode: str

    # ============================================================
    # INVESTIGATION EVIDENCE
    # ============================================================
    logs: list[dict[str, Any]]
    metrics: list[dict[str, Any]]
    database_events: list[dict[str, Any]]
    deployments: list[dict[str, Any]]

    # ============================================================
    # RAG / KNOWLEDGE BASE
    # ============================================================
    rag_context: list[dict[str, Any]]
    rag_query: str
    rag_sources: list[str]

    # ============================================================
    # AGENT FINDINGS
    # ============================================================
    log_findings: list[str]
    metrics_findings: list[str]
    database_findings: list[str]
    deployment_findings: list[str]

    # ============================================================
    # CORRELATION AND HYPOTHESES
    # ============================================================
    correlations: list[str]
    hypotheses: list[dict[str, Any]]

    # ============================================================
    # ROOT-CAUSE ANALYSIS
    # ============================================================
    root_cause: str
    confidence: float
    root_cause_rationale: str

    # ============================================================
    # CRITIC REVIEW
    # ============================================================
    critic_feedback: str
    critic_verdict: str

    # Possible values:
    # - PASS
    # - REWORK
    critic_confidence: float

    # ============================================================
    # HUMAN-IN-THE-LOOP
    # ============================================================
    human_decision: str
    human_feedback: str
    human_approval_required: bool
    human_reviewed: bool

    # Possible human decisions:
    # - APPROVE
    # - REJECT
    # - MODIFY
    # - None / empty before review

    # ============================================================
    # WORKFLOW CONTROL
    # ============================================================
    next_action: str
    investigation_status: str
    iteration: int
    max_iterations: int

    # ============================================================
    # FINAL RESULT
    # ============================================================
    final_report: str

    # ============================================================
    # AGENT EXECUTION HISTORY
    # ============================================================
    execution_history: list[dict[str, Any]]