from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import AegisIncidentState
from app.llm import get_llm


CRITIC_SYSTEM_PROMPT = """
You are an incident RCA critic.

Evaluate whether the proposed root cause is sufficiently supported.

PASS when:
- Evidence directly matches the proposed cause.
- Multiple findings support the same explanation.
- Confidence is reasonable.
- No strong contradictory evidence exists.

REWORK only when:
- The RCA is poorly supported.
- Evidence contradicts it.
- Confidence is clearly unreasonable.
- The RCA does not explain the incident symptoms.

Missing evidence alone does NOT require REWORK.

Return ONLY valid JSON:

{
  "verdict": "PASS",
  "confidence_valid": true,
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
        "root_cause": state.get("root_cause", ""),
        "confidence": state.get("confidence", 0.0),
        "rationale": state.get(
            "root_cause_rationale",
            "",
        ),
        "alternative": alternative.get(
            "root_cause",
            "",
        ),
        "correlations": state.get(
            "correlations",
            [],
        ),
    }

    prompt = (
        "Review this incident RCA.\n\n"
        + json.dumps(
            evidence,
            separators=(",", ":"),
        )
        + "\n\n"
        "The incident has HTTP 500 errors caused by "
        "database connection failures. Determine whether "
        "the proposed RCA is sufficiently supported. "
        "Return ONLY JSON."
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
        ).upper()

        if verdict not in {
            "PASS",
            "REWORK",
        }:
            verdict = "REWORK"

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

        if "429" in error_text or "rate_limit" in error_text.lower():
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
    print("STATUS:")
    print(result.get("investigation_status"))
    print()
    print("NEXT ACTION:")
    print(result.get("next_action"))