from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import AegisIncidentState
from app.llm import llm


REPORT_SYSTEM_PROMPT = """
You are the Final Incident Report Agent in an AI Software Incident Commander.

Create a concise, professional incident report from the investigation.

Use ONLY the evidence provided.

Do not invent facts.

IMPORTANT:
- Investigation evidence is the primary source of truth.
- RAG knowledge is supporting context only.
- Do not present RAG documents as proof that something happened.
- Clearly distinguish observed evidence from hypotheses.
- Do not claim that recommended actions were already performed.
- Do not hide uncertainty.
- Respect the Critic Agent's verdict.
- Respect the Human-in-the-Loop decision.
- If the human rejected or requested rework, clearly state that the
  root cause was not approved as final.

The report must contain these sections:

# Incident Report

## Incident
Include:
- Incident ID
- Service
- Description
- Severity if available

## Executive Summary
Briefly explain what happened and the current investigation conclusion.

## Impact
Describe the observed technical impact using only available evidence.

## Timeline
Present important events in chronological order when timestamps are available.

## Evidence
Summarize important findings from:
- Logs
- Metrics
- Database
- Deployments
- Correlations

## RAG Knowledge
Briefly mention relevant knowledge-base documents that supported the investigation.
Do not treat them as direct incident evidence.

## Root Cause
State the most likely root cause and confidence.
Clearly indicate whether the root cause is proven or remains a hypothesis.

## Critic Review
Summarize:
- Critic verdict
- Critic feedback
- Missing evidence
- Contradictory evidence if any

## Human Review
Summarize:
- Human decision
- Human feedback
- Whether the root cause was approved

## Alternative Hypothesis
Mention the alternative explanation if available.

## Recommended Actions
Provide practical next steps based on the evidence and identified gaps.

Recommendations must be clearly presented as recommendations.
Do not claim that an action was performed.
"""


def _extract_content(response) -> str:
    """Safely extract text from an LLM response."""

    content = getattr(response, "content", "")

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(
                        str(item.get("text", ""))
                    )
            else:
                parts.append(str(item))

        return "".join(parts).strip()

    return str(content).strip()


def _format_rag_context(
    rag_context: list[dict],
) -> list[dict]:
    """Keep only useful metadata from retrieved RAG documents."""

    formatted = []

    for item in rag_context:
        formatted.append(
            {
                "filename": item.get(
                    "filename",
                    "",
                ),
                "category": item.get(
                    "category",
                    "",
                ),
                "source": item.get(
                    "source",
                    "",
                ),
            }
        )

    return formatted


def report_agent_node(
    state: AegisIncidentState,
) -> AegisIncidentState:
    """
    Generate the final incident report.

    The report incorporates:
    - Investigation evidence
    - RAG knowledge references
    - Root-cause analysis
    - Critic review
    - Human-in-the-loop decision
    """

    rag_context = state.get(
        "rag_context",
        [],
    )

    evidence = {
        "incident": {
            "incident_id": state.get(
                "incident_id"
            ),
            "description": state.get(
                "description"
            ),
            "service": state.get(
                "service"
            ),
            "severity": state.get(
                "severity"
            ),
        },

        "log_findings": state.get(
            "log_findings",
            [],
        ),

        "metrics_findings": state.get(
            "metrics_findings",
            [],
        ),

        "database_findings": state.get(
            "database_findings",
            [],
        ),

        "deployment_findings": state.get(
            "deployment_findings",
            [],
        ),

        "correlations": state.get(
            "correlations",
            [],
        ),

        "root_cause": state.get(
            "root_cause",
            "",
        ),

        "confidence": state.get(
            "confidence",
            0.0,
        ),

        "hypotheses": state.get(
            "hypotheses",
            [],
        ),

        "critic": {
            "verdict": state.get(
                "critic_verdict",
                "",
            ),
            "feedback": state.get(
                "critic_feedback",
                "",
            ),
            "confidence_valid": state.get(
                "critic_confidence_valid",
                False,
            ),
            "missing_evidence": state.get(
                "critic_missing_evidence",
                [],
            ),
            "contradictory_evidence": state.get(
                "critic_contradictory_evidence",
                [],
            ),
            "rag_support": state.get(
                "critic_rag_support",
                [],
            ),
        },

        "human_review": {
            "decision": state.get(
                "human_decision",
                "",
            ),
            "feedback": state.get(
                "human_feedback",
                "",
            ),
            "required": state.get(
                "human_review_required",
                True,
            ),
        },

        "rag_knowledge": _format_rag_context(
            rag_context
        ),
    }

    prompt = f"""
Generate the final incident report from this investigation:

{json.dumps(evidence, indent=2)}

Remember:

1. Do not invent evidence.
2. Do not treat RAG knowledge as direct proof.
3. Clearly state uncertainty.
4. Respect the Critic verdict.
5. Respect the Human-in-the-Loop decision.
6. Recommendations are proposed actions, not completed actions.
"""

    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=REPORT_SYSTEM_PROMPT
                ),
                HumanMessage(
                    content=prompt
                ),
            ]
        )

        report = _extract_content(response)

        if not report:
            raise ValueError(
                "The report agent returned an empty report."
            )

        execution_history = list(
            state.get(
                "execution_history",
                [],
            )
        )

        execution_history.append(
            {
                "agent": "Report",
                "status": "completed",
                "message": (
                    "Final incident report generated."
                ),
            }
        )

        return {
            "final_report": report,
            "investigation_status": (
                "incident_report_complete"
            ),
            "next_action": "complete",
            "execution_history": (
                execution_history
            ),
        }

    except Exception as exc:

        fallback_report = f"""
# Incident Report

## Incident

- **Incident ID:** {state.get("incident_id", "Unknown")}
- **Service:** {state.get("service", "Unknown")}
- **Description:** {state.get("description", "Unknown")}
- **Severity:** {state.get("severity", "Unknown")}

## Executive Summary

The incident investigation identified a likely root-cause hypothesis
using the collected investigation evidence.

The conclusion remains subject to the Critic Agent review and
Human-in-the-Loop decision.

## Impact

### Logs
{state.get("log_findings", [])}

### Metrics
{state.get("metrics_findings", [])}

### Database
{state.get("database_findings", [])}

### Deployments
{state.get("deployment_findings", [])}

## Correlations

{state.get("correlations", [])}

## RAG Knowledge

The investigation retrieved the following knowledge-base documents:

{_format_rag_context(rag_context)}

These documents are supporting knowledge and are not direct proof
of the incident cause.

## Root Cause

{state.get("root_cause", "Unable to determine root cause.")}

**Confidence:** {state.get("confidence", 0.0):.0%}

## Critic Review

**Verdict:** {state.get("critic_verdict", "Unknown")}

{state.get("critic_feedback", "No critic feedback available.")}

### Missing Evidence

{state.get("critic_missing_evidence", [])}

### Contradictory Evidence

{state.get("critic_contradictory_evidence", [])}

## Human Review

**Decision:** {state.get("human_decision", "Pending")}

**Feedback:** {state.get("human_feedback", "No human feedback available.")}

## Alternative Hypothesis

{next(
    (
        h.get("root_cause", "")
        for h in state.get("hypotheses", [])
        if h.get("type") == "alternative"
    ),
    "No alternative hypothesis available."
)}

## Recommended Actions

1. Review the missing evidence identified by the Critic Agent.
2. Validate the root-cause hypothesis against production evidence.
3. Review relevant RAG runbooks and previous incidents.
4. Perform appropriate remediation after human approval.

## Report Generation Error

{exc}
"""

        execution_history = list(
            state.get(
                "execution_history",
                [],
            )
        )

        execution_history.append(
            {
                "agent": "Report",
                "status": "completed",
                "message": (
                    "Fallback incident report generated "
                    "because LLM report generation failed."
                ),
            }
        )

        return {
            "final_report": (
                fallback_report.strip()
            ),
            "investigation_status": (
                "incident_report_complete"
            ),
            "next_action": "complete",
            "execution_history": (
                execution_history
            ),
        }