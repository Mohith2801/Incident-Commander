from __future__ import annotations

import re
from typing import Any

from app.llm import get_llm
from agents.state import AegisIncidentState


def _format_rag_context(
    rag_context: list[dict[str, Any]],
) -> str:
    if not rag_context:
        return "No RAG documents retrieved."

    sections = []

    for i, document in enumerate(rag_context, 1):
        content = str(
            document.get("content", "")
        )

        # Keep RAG context small.
        content = content[:2500]

        sections.append(
            f"Document {i}: "
            f"{document.get('filename', 'Unknown')}\n"
            f"Category: {document.get('category', 'Unknown')}\n"
            f"{content}"
        )

    return "\n\n".join(sections)


def _parse_confidence(value: str) -> float:
    value = value.strip()

    match = re.search(
        r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)",
        value,
    )

    if not match:
        return 0.0

    try:
        number = float(match.group(0))
    except ValueError:
        return 0.0

    if "%" in value or number > 1:
        number /= 100.0

    return max(0.0, min(1.0, number))


def _extract_content(response) -> str:
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


def root_cause_agent_node(
    state: AegisIncidentState,
) -> dict:
    """
    Generate the most likely root cause using the
    summarized investigation evidence.

    The prompt intentionally avoids sending all raw
    data and full RAG documents to reduce token usage.
    """

    llm = get_llm()

    log_findings = state.get(
        "log_findings",
        [],
    )

    metrics_findings = state.get(
        "metrics_findings",
        [],
    )

    database_findings = state.get(
        "database_findings",
        [],
    )

    deployment_findings = state.get(
        "deployment_findings",
        [],
    )

    correlations = state.get(
        "correlations",
        [],
    )

    rag_context = state.get(
        "rag_context",
        [],
    )

    human_feedback = state.get(
        "human_feedback",
        "",
    )

    rag_text = _format_rag_context(rag_context)
    rag_text = _format_rag_context(
        rag_context
    )

    prompt = f"""
You are a Root Cause Analysis Agent.

Analyze the incident using ONLY the evidence below.

IMPORTANT:
- Do not invent evidence.
- RAG documents are supporting knowledge, not proof.
- Correlation is not automatically causation.
- Prefer the hypothesis supported by multiple independent evidence sources.
- Do not use confidence 0.0 merely because absolute proof is unavailable.
- If several evidence sources strongly support a probable cause,
  use a reasonable confidence such as 0.70-0.90.
- Confidence must be between 0 and 1.
- Keep the response concise.

HUMAN REVIEW RULES:
- If human review feedback is provided, use it when revising the RCA.
- Re-evaluate the previous root-cause hypothesis using the feedback.
- Do not blindly accept the human feedback if it conflicts with the evidence.
- Preserve evidence-supported conclusions.
- If the human reviewer requests additional investigation,
  clearly reflect the requested evidence in MISSING_EVIDENCE.
- The revised RCA should improve on the previous RCA rather than
  simply repeating it.

INCIDENT
ID: {state.get("incident_id", "")}
Service: {state.get("service", "")}
Description: {state.get("description", "")}
Severity: {state.get("severity", "")}
HUMAN REVIEW FEEDBACK
{human_feedback if human_feedback else "No human rework feedback provided."}

LOG FINDINGS
{log_findings}

METRICS FINDINGS
{metrics_findings}

DATABASE FINDINGS
{database_findings}

DEPLOYMENT FINDINGS
{deployment_findings}

CORRELATIONS
{correlations}

RAG KNOWLEDGE
{rag_text}

Return ONLY:

ROOT_CAUSE:
<most likely root cause>

CONFIDENCE:
<decimal between 0 and 1>

ALTERNATIVE:
<realistic alternative hypothesis>

ALTERNATIVE_CONFIDENCE:
<decimal between 0 and 1>

RATIONALE:
<short explanation based on the evidence>

MISSING_EVIDENCE:
<short list of evidence needed for stronger confirmation>
"""

    response = llm.invoke(prompt)

    text = _extract_content(response)

    root_cause = ""
    confidence = 0.0
    alternative = ""
    alternative_confidence = 0.0
    rationale = ""
    missing_evidence = ""

    current_section = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        upper = line.upper()

        if upper.startswith("ROOT_CAUSE:"):
            current_section = "root_cause"
            root_cause = line.split(
                ":", 1
            )[1].strip()

        elif upper.startswith("CONFIDENCE:"):
            current_section = "confidence"
            confidence = _parse_confidence(
                line.split(":", 1)[1]
            )

        elif upper.startswith(
            "ALTERNATIVE_CONFIDENCE:"
        ):
            current_section = (
                "alternative_confidence"
            )
            alternative_confidence = (
                _parse_confidence(
                    line.split(":", 1)[1]
                )
            )

        elif upper.startswith("ALTERNATIVE:"):
            current_section = "alternative"
            alternative = line.split(
                ":", 1
            )[1].strip()

        elif upper.startswith("RATIONALE:"):
            current_section = "rationale"
            rationale = line.split(
                ":", 1
            )[1].strip()

        elif upper.startswith(
            "MISSING_EVIDENCE:"
        ):
            current_section = (
                "missing_evidence"
            )
            missing_evidence = line.split(
                ":", 1
            )[1].strip()

        elif current_section == "root_cause":
            root_cause += " " + line

        elif current_section == "alternative":
            alternative += " " + line

        elif current_section == "rationale":
            rationale += " " + line

        elif current_section == "missing_evidence":
            missing_evidence += " " + line

    confidence = max(
        0.0,
        min(1.0, confidence),
    )
    evidence_confidence = _evidence_confidence(
        state
    )

    if evidence_confidence > confidence:
        confidence = evidence_confidence

    alternative_confidence = max(
        0.0,
        min(
            1.0,
            alternative_confidence,
        ),
    )

    if not root_cause:
        root_cause = (
            "The available evidence does not "
            "establish a root cause."
        )

    if not alternative:
        alternative = (
            "A downstream database or external "
            "dependency may have caused the failure."
        )

    hypotheses = [
        {
            "type": "primary",
            "root_cause": root_cause,
            "confidence": confidence,
            "rationale": rationale,
            "missing_evidence": missing_evidence,
        },
        {
            "type": "alternative",
            "root_cause": alternative,
            "confidence": alternative_confidence,
        },
    ]

    message = (
        "Primary root-cause hypothesis generated "
        f"with {confidence:.0%} confidence."
    )

    return {
        "root_cause": root_cause,
        "confidence": confidence,
        "hypotheses": hypotheses,
        "root_cause_rationale": rationale,
        "missing_evidence": missing_evidence,
        "root_cause_agent_message": message,
        "investigation_status": (
            "root_cause_analysis_complete"
        ),
        "next_action": "critic_review",
    }


if __name__ == "__main__":
    state: AegisIncidentState = {
        "incident_id": "INC-001",
        "description": "API returning HTTP 500 errors",
        "service": "api",
        "severity": "SEV-2",
        "logs": [],
        "metrics": [],
        "database_events": [],
        "deployments": [],
        "log_findings": [],
        "metrics_findings": [],
        "database_findings": [],
        "deployment_findings": [],
        "correlations": [],
        "rag_context": [],
    }

    result = root_cause_agent_node(state)

    print("ROOT CAUSE:")
    print(result.get("root_cause"))

    print()
    print("CONFIDENCE:")
    print(result.get("confidence"))

    print()
    print("ALTERNATIVE:")
    print(
        result.get(
            "hypotheses",
            [{}],
        )[1].get(
            "root_cause",
            "",
        )
    )
def _evidence_confidence(
    state: AegisIncidentState,
) -> float:

    score = 0.0

    logs = state.get(
        "log_findings",
        []
    )

    database = state.get(
        "database_findings",
        []
    )

    deployments = state.get(
        "deployment_findings",
        []
    )

    correlations = state.get(
        "correlations",
        []
    )

    # HTTP 500 / database timeout evidence
    if logs:
        score += 0.20

    # Database failure / pool exhaustion evidence
    if database:
        score += 0.25

    # Deployment evidence
    if deployments:
        score += 0.20

    # Temporal / cross-source correlation
    if correlations:
        score += 0.25

    # Additional supporting RAG knowledge
    if state.get("rag_context"):
        score += 0.10

    return min(
        0.95,
        score
    )