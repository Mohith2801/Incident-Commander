from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import AegisIncidentState
from app.llm import get_llm


CRITIC_SYSTEM_PROMPT = """
You are an incident RCA critic.

Evaluate whether the proposed root cause is sufficiently supported
by the actual incident evidence provided.

PASS when:
- Evidence directly supports the proposed cause.
- Multiple findings support the same explanation when available.
- Confidence is reasonable.
- No strong contradictory evidence exists.
- The proposed RCA explains the incident symptoms.

REWORK only when:
- The RCA is poorly supported.
- Evidence contradicts it.
- Confidence is clearly unreasonable.
- The RCA does not explain the incident symptoms.

Missing evidence alone does NOT require REWORK.

Do not assume a specific root cause.
Do not invent evidence.
Evaluate only the incident and evidence provided.

Return ONLY valid JSON:

{
  "verdict": "PASS",
  "confidence_valid": true,
  "confidence": 0.0,
  "feedback": "brief assessment",
  "missing_evidence": [],
  "contradictory_evidence": []
}
"""


def _extract_content(response) -> str:
    content = getattr(response, "content", "")

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))

        return "".join(parts).strip()

    return str(content).strip()


def _parse_confidence(value) -> float:
    try:
        if isinstance(value, str):
            value = value.strip()

            if "%" in value:
                number = float(value.replace("%", "").strip())
                number /= 100.0
            else:
                number = float(value)
        else:
            number = float(value)

    except (TypeError, ValueError):
        return 0.0

    if number > 1:
        number /= 100.0

    return max(0.0, min(1.0, number))


def _clean_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


def critic_agent_node(
    state: AegisIncidentState,
) -> dict:

    hypotheses = state.get("hypotheses", [])

    alternative = (
        hypotheses[1]
        if len(hypotheses) > 1
        else {}
    )

    evidence = {
        "incident_id": state.get(
            "incident_id",
            "",
        ),
        "description": state.get(
            "description",
            "",
        ),
        "service": state.get(
            "service",
            "",
        ),
        "severity": state.get(
            "severity",
            "",
        ),
        "root_cause": state.get(
            "root_cause",
            "",
        ),
        "confidence": state.get(
            "confidence",
            0.0,
        ),
        "rationale": state.get(
            "root_cause_rationale",
            "",
        ),
        "alternative": alternative.get(
            "root_cause",
            "",
        ),
        "alternative_confidence": alternative.get(
            "confidence",
            0.0,
        ),
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
        "rag_context": state.get(
            "rag_context",
            [],
        ),
    }

    prompt = (
        "Review the following incident RCA.\n\n"
        + json.dumps(
            evidence,
            separators=(",", ":"),
            default=str,
        )
        + "\n\n"
        "Evaluate the proposed root cause using ONLY "
        "the incident evidence provided above. "
        "Do not assume any specific cause. "
        "Return ONLY valid JSON."
    )

    try:
        llm = get_llm()

        response = llm.invoke(
            [
                SystemMessage(
                    content=CRITIC_SYSTEM_PROMPT
                ),
                HumanMessage(
                    content=prompt
                ),
            ]
        )

        content = _extract_content(response)
        result = _clean_json(content)

        verdict = str(
            result.get(
                "verdict",
                "REWORK",
            )
        ).upper().strip()

        if verdict not in {
            "PASS",
            "REWORK",
        }:
            verdict = "REWORK"

        confidence_valid = result.get(
            "confidence_valid",
            False,
        )

        if isinstance(
            confidence_valid,
            str,
        ):
            confidence_valid = (
                confidence_valid.lower().strip()
                == "true"
            )
        else:
            confidence_valid = bool(
                confidence_valid
            )

        critic_confidence = _parse_confidence(
            result.get(
                "confidence",
                0.0,
            )
        )

        feedback = str(
            result.get(
                "feedback",
                "No critic feedback provided.",
            )
        )

        missing_evidence = result.get(
            "missing_evidence",
            [],
        )

        contradictory_evidence = result.get(
            "contradictory_evidence",
            [],
        )

        if not isinstance(
            missing_evidence,
            list,
        ):
            missing_evidence = [
                str(missing_evidence)
            ]

        if not isinstance(
            contradictory_evidence,
            list,
        ):
            contradictory_evidence = [
                str(contradictory_evidence)
            ]

        critic_feedback = (
            f"Verdict: {verdict}. {feedback}"
        )

        if missing_evidence:
            critic_feedback += (
                " Missing evidence: "
                + "; ".join(
                    str(x)
                    for x in missing_evidence
                )
                + "."
            )

        if contradictory_evidence:
            critic_feedback += (
                " Contradictory evidence: "
                + "; ".join(
                    str(x)
                    for x in contradictory_evidence
                )
                + "."
            )

        return {
            "critic_verdict": verdict,
            "critic_confidence": critic_confidence,
            "critic_confidence_valid": (
                confidence_valid
            ),
            "critic_missing_evidence": (
                missing_evidence
            ),
            "critic_contradictory_evidence": (
                contradictory_evidence
            ),
            "critic_feedback": critic_feedback,
            "investigation_status": (
                "critic_review_complete"
            ),
            "next_action": (
                "generate_final_report"
                if verdict == "PASS"
                else "review_findings"
            ),
        }

    except Exception as exc:
        error_text = str(exc)

        if (
            "429" in error_text
            or "rate_limit" in error_text.lower()
        ):
            feedback = (
                "Critic review could not be completed "
                "because the Groq API rate limit was reached. "
                "The RCA itself was generated successfully."
            )
        else:
            feedback = (
                "Critic Agent failed: "
                + error_text
            )

        return {
            "critic_verdict": "ERROR",
            "critic_confidence": 0.0,
            "critic_confidence_valid": False,
            "critic_missing_evidence": [],
            "critic_contradictory_evidence": [],
            "critic_feedback": feedback,
            "investigation_status": (
                "critic_review_failed"
            ),
            "next_action": "review_findings",
        }


if __name__ == "__main__":
    state: AegisIncidentState = {
        "incident_id": "INC-001",
        "description": "API returning HTTP 500 errors",
        "service": "api",
        "severity": "SEV-2",
        "root_cause": (
            "Database connection pool misconfiguration "
            "introduced in deployment v2.4.1, leading to "
            "connection pool exhaustion and subsequent "
            "HTTP 500 errors."
        ),
        "confidence": 0.95,
        "root_cause_rationale": (
            "Database connection timeouts and pool "
            "exhaustion occurred during the incident."
        ),
        "hypotheses": [
            {
                "type": "primary",
                "root_cause": (
                    "Database connection pool "
                    "misconfiguration."
                ),
                "confidence": 0.95,
            },
            {
                "type": "alternative",
                "root_cause": (
                    "A downstream database failure."
                ),
                "confidence": 0.2,
            },
        ],
        "correlations": [
            "Deployment v2.4.1 preceded database failures.",
            "Database pool exhaustion coincided with HTTP 500 errors.",
        ],
    }

    result = critic_agent_node(state)

    print("CRITIC RESULT:")
    print(result.get("critic_feedback"))

    print()
    print("VERDICT:")
    print(result.get("critic_verdict"))

    print()
    print("CRITIC CONFIDENCE:")
    print(result.get("critic_confidence"))

    print()
    print("CONFIDENCE VALID:")
    print(result.get("critic_confidence_valid"))

    print()
    print("STATUS:")
    print(result.get("investigation_status"))

    print()
    print("NEXT ACTION:")
    print(result.get("next_action"))