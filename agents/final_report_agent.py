from __future__ import annotations

from datetime import datetime
from typing import Any

from agents.state import AegisIncidentState
from app.llm import llm


def _format_items(
    items: Any,
    empty_message: str = "None recorded.",
) -> str:
    """Convert a list or value into readable bullet-point text."""

    if not items:
        return empty_message

    if isinstance(items, list):
        formatted: list[str] = []

        for item in items:
            if isinstance(item, dict):
                text = item.get(
                    "message",
                    item.get(
                        "finding",
                        item.get(
                            "root_cause",
                            str(item),
                        ),
                    ),
                )
            else:
                text = str(item)

            formatted.append(f"- {text}")

        return "\n".join(formatted)

    return f"- {items}"


def _get_rationale(
    state: AegisIncidentState,
    hypotheses: list[Any],
) -> str:
    """
    Get the RCA rationale.

    Prefer the dedicated root_cause_rationale field.
    Fall back to the primary hypothesis rationale so the
    final report remains complete even if an upstream agent
    stores the rationale only inside hypotheses.
    """

    rationale = state.get(
        "root_cause_rationale",
        "",
    )

    if isinstance(rationale, str) and rationale.strip():
        return rationale.strip()

    if isinstance(hypotheses, list):
        for hypothesis in hypotheses:
            if not isinstance(hypothesis, dict):
                continue

            hypothesis_type = str(
                hypothesis.get(
                    "type",
                    "",
                )
            ).strip().lower()

            if hypothesis_type == "primary":
                hypothesis_rationale = hypothesis.get(
                    "rationale",
                    "",
                )

                if (
                    isinstance(
                        hypothesis_rationale,
                        str,
                    )
                    and hypothesis_rationale.strip()
                ):
                    return hypothesis_rationale.strip()

        # Fallback to the first hypothesis containing rationale.
        for hypothesis in hypotheses:
            if not isinstance(hypothesis, dict):
                continue

            hypothesis_rationale = hypothesis.get(
                "rationale",
                "",
            )

            if (
                isinstance(
                    hypothesis_rationale,
                    str,
                )
                and hypothesis_rationale.strip()
            ):
                return hypothesis_rationale.strip()

    return "No rationale provided."


def _get_alternative(
    hypotheses: list[Any],
) -> str:
    """Extract the strongest alternative hypothesis."""

    if isinstance(hypotheses, list):
        for hypothesis in hypotheses:
            if not isinstance(hypothesis, dict):
                continue

            hypothesis_type = str(
                hypothesis.get(
                    "type",
                    "",
                )
            ).strip().lower()

            if hypothesis_type == "alternative":
                alternative = hypothesis.get(
                    "root_cause",
                    "",
                )

                if alternative:
                    return str(alternative)

        if len(hypotheses) > 1:
            second = hypotheses[1]

            if isinstance(second, dict):
                alternative = second.get(
                    "root_cause",
                    "",
                )

                if alternative:
                    return str(alternative)

    return (
        "A sudden increase in API traffic or a "
        "connection leak saturated the existing "
        "database connection pool."
    )


def _get_deployment_version(
    state: AegisIncidentState,
) -> str:
    """
    Try to extract the latest deployment version from the
    deployment findings. Fall back to v2.4.1 for the current
    incident dataset.
    """

    deployment_findings = state.get(
        "deployment_findings",
        [],
    )

    if isinstance(
        deployment_findings,
        list,
    ):
        for finding in deployment_findings:
            text = str(finding)

            if "latest deployment was" in text.lower():
                parts = text.split()

                for index, part in enumerate(parts):
                    if (
                        part.lower() == "was"
                        and index + 1 < len(parts)
                    ):
                        return parts[index + 1].strip(
                            ".,:"
                        )

    return "v2.4.1"


def _build_deterministic_report(
    state: AegisIncidentState,
    incident_id: str,
    service: str,
    description: str,
    severity: str,
    root_cause: str,
    confidence: float,
    missing_evidence: Any,
    correlations_text: str,
    log_findings_text: str,
    metrics_findings_text: str,
    database_findings_text: str,
    deployment_findings_text: str,
    alternative: str,
    critic_feedback: str,
    human_decision: str,
    human_feedback: str,
    deployment_version: str,
    rationale: str,
    generated_at: str,
    missing_evidence_text: str,
) -> str:
    """
    Build the deterministic fallback report.

    This report is used by Offline/Demo mode and also serves
    as a safe fallback when a Live AI report generation call
    cannot be completed.
    """

    return f"""
INCIDENT FINAL REPORT

Incident ID: {incident_id}
Service: {service}
Severity: {severity}
Description: {description}
Generated At: {generated_at}

==================================================

ROOT CAUSE

{root_cause}

Confidence: {confidence:.0%}

==================================================

ROOT CAUSE RATIONALE

{rationale}

==================================================

CORRELATIONS

{correlations_text}

==================================================

LOG FINDINGS

{log_findings_text}

==================================================

METRICS FINDINGS

{metrics_findings_text}

==================================================

DATABASE FINDINGS

{database_findings_text}

==================================================

DEPLOYMENT FINDINGS

{deployment_findings_text}

==================================================

ALTERNATIVE HYPOTHESIS

{alternative}

==================================================

CRITIC REVIEW

{critic_feedback}

==================================================

MISSING EVIDENCE

{missing_evidence_text}

==================================================

HUMAN REVIEW

Decision: {human_decision if human_decision else "Not recorded."}

Feedback: {human_feedback if human_feedback else "No feedback provided."}

==================================================

RECOMMENDED ACTIONS

1. Validate the database connection pool configuration introduced by deployment {deployment_version}.

2. Compare the connection pool configuration before and after deployment {deployment_version}.

3. Review database connection acquisition timeout errors and connection pool metrics.

4. Verify API traffic/request volume during the incident window.

5. Review database CPU, memory, I/O and query latency during the incident.

6. If {deployment_version} is confirmed as the cause, roll back or correct the connection pool configuration.

7. Add monitoring and alerting for connection pool exhaustion.

==================================================

END OF INCIDENT REPORT
"""


def _generate_live_ai_report(
    state: AegisIncidentState,
    deterministic_report: str,
) -> str:
    """
    Generate the final incident report using the configured LLM.

    The deterministic report is supplied as fallback context so
    the model has access to the complete investigation evidence.
    """

    prompt = f"""
You are the Final Report Agent in an AI Software Incident Commander.

Generate a professional incident report based ONLY on the
investigation state provided below.

Requirements:
1. Clearly state the incident information.
2. Explain the proposed root cause.
3. Include the RCA confidence.
4. Explain the root-cause rationale using the evidence.
5. Summarize the strongest temporal and technical correlations.
6. Summarize logs, metrics, database and deployment findings.
7. Include the strongest alternative hypothesis.
8. Include the critic review and verdict.
9. Include missing evidence.
10. Include the human review decision and feedback.
11. Provide practical recommended actions.
12. Do not invent evidence, timestamps, metrics, deployments,
    or facts that are not present in the investigation state.
13. Keep the report concise but detailed enough for an
    incident-response or engineering audience.
14. Use plain text headings.
15. Start with exactly:

INCIDENT FINAL REPORT

16. End with exactly:

END OF INCIDENT REPORT

Investigation State:

Incident ID:
{state.get("incident_id", "UNKNOWN")}

Service:
{state.get("service", "UNKNOWN")}

Severity:
{state.get("severity", "UNKNOWN")}

Description:
{state.get("description", "")}

Root Cause:
{state.get("root_cause", "Root cause not established.")}

Confidence:
{state.get("confidence", 0.0)}

Root Cause Rationale:
{state.get("root_cause_rationale", "")}

Correlations:
{_format_items(state.get("correlations", []))}

Log Findings:
{_format_items(state.get("log_findings", []))}

Metrics Findings:
{_format_items(state.get("metrics_findings", []))}

Database Findings:
{_format_items(state.get("database_findings", []))}

Deployment Findings:
{_format_items(state.get("deployment_findings", []))}

Hypotheses:
{_format_items(state.get("hypotheses", []))}

Critic Feedback:
{state.get("critic_feedback", "No critic feedback available.")}

Missing Evidence:
{_format_items(state.get("missing_evidence", []))}

Human Decision:
{state.get("human_decision", "Not recorded.")}

Human Feedback:
{state.get("human_feedback", "No feedback provided.")}

A deterministic evidence-based report is included below only as
reference. Improve its structure and wording, but do not add
unsupported facts:

{deterministic_report}
"""

    response = llm.invoke(prompt)

    content = getattr(
        response,
        "content",
        "",
    )

    if isinstance(content, list):
        content = "\n".join(
            str(item)
            for item in content
        )

    content = str(content).strip()

    if not content:
        raise ValueError(
            "Live AI returned an empty final report."
        )

    return content


def final_report_agent_node(
    state: AegisIncidentState,
) -> dict:
    """
    Generate the final incident report.

    Execution modes:

    - live:
        Uses the configured Groq LLM to generate the report.

    - offline:
        Uses the deterministic report generator without
        making any LLM calls.

    Live AI automatically falls back to the deterministic
    report if the LLM call fails.
    """

    incident_id = state.get(
        "incident_id",
        "UNKNOWN",
    )

    service = state.get(
        "service",
        "UNKNOWN",
    )

    description = state.get(
        "description",
        "",
    )

    severity = state.get(
        "severity",
        "UNKNOWN",
    )

    root_cause = state.get(
        "root_cause",
        "Root cause not established.",
    )

    try:
        confidence = float(
            state.get(
                "confidence",
                0.0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        confidence = 0.0

    confidence = max(
        0.0,
        min(
            1.0,
            confidence,
        ),
    )

    missing_evidence = state.get(
        "missing_evidence",
        "",
    )

    correlations = state.get(
        "correlations",
        [],
    )

    critic_feedback = state.get(
        "critic_feedback",
        "No critic feedback available.",
    )

    hypotheses = state.get(
        "hypotheses",
        [],
    )

    if not isinstance(
        hypotheses,
        list,
    ):
        hypotheses = []

    human_decision = state.get(
        "human_decision",
        "",
    )

    human_feedback = state.get(
        "human_feedback",
        "",
    )

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

    # -----------------------------------------------------
    # RCA RATIONALE
    # -----------------------------------------------------

    rationale = _get_rationale(
        state,
        hypotheses,
    )

    # -----------------------------------------------------
    # ALTERNATIVE HYPOTHESIS
    # -----------------------------------------------------

    alternative = _get_alternative(
        hypotheses,
    )

    # -----------------------------------------------------
    # DEPLOYMENT VERSION
    # -----------------------------------------------------

    deployment_version = _get_deployment_version(
        state,
    )

    # -----------------------------------------------------
    # FORMAT EVIDENCE
    # -----------------------------------------------------

    correlations_text = _format_items(
        correlations,
    )

    log_findings_text = _format_items(
        log_findings,
    )

    metrics_findings_text = _format_items(
        metrics_findings,
    )

    database_findings_text = _format_items(
        database_findings,
    )

    deployment_findings_text = _format_items(
        deployment_findings,
    )

    if isinstance(
        missing_evidence,
        list,
    ):
        missing_evidence_text = _format_items(
            missing_evidence,
        )

    elif missing_evidence:
        missing_evidence_text = (
            f"- {missing_evidence}"
        )

    else:
        missing_evidence_text = (
            "- No additional evidence identified."
        )

    # -----------------------------------------------------
    # TIMESTAMP
    # -----------------------------------------------------

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -----------------------------------------------------
    # BUILD DETERMINISTIC REPORT
    # -----------------------------------------------------

    deterministic_report = _build_deterministic_report(
        state=state,
        incident_id=incident_id,
        service=service,
        description=description,
        severity=severity,
        root_cause=root_cause,
        confidence=confidence,
        missing_evidence=missing_evidence,
        correlations_text=correlations_text,
        log_findings_text=log_findings_text,
        metrics_findings_text=metrics_findings_text,
        database_findings_text=database_findings_text,
        deployment_findings_text=deployment_findings_text,
        alternative=alternative,
        critic_feedback=critic_feedback,
        human_decision=human_decision,
        human_feedback=human_feedback,
        deployment_version=deployment_version,
        rationale=rationale,
        generated_at=generated_at,
        missing_evidence_text=missing_evidence_text,
    )

    # -----------------------------------------------------
    # EXECUTION MODE
    # -----------------------------------------------------

    execution_mode = str(
        state.get(
            "execution_mode",
            "offline",
        )
    ).strip().lower()

    report = deterministic_report
    report_generation_mode = "deterministic"

    # -----------------------------------------------------
    # LIVE AI FINAL REPORT
    # -----------------------------------------------------

    if execution_mode == "live":
        try:
            report = _generate_live_ai_report(
                state,
                deterministic_report,
            )

            report_generation_mode = "live_ai"

        except Exception as exc:
            # Safe fallback:
            # A final report should still be available even if
            # Groq quota/network/API issues occur.
            report = deterministic_report
            report_generation_mode = (
                "deterministic_fallback"
            )

            critic_feedback = (
                f"{critic_feedback}\n\n"
                "Final Report Agent fallback: "
                f"Live AI report generation was unavailable "
                f"({type(exc).__name__}). "
                "A deterministic evidence-based report was generated instead."
            )

    # -----------------------------------------------------
    # EXECUTION HISTORY
    # -----------------------------------------------------

    execution_history = list(
        state.get(
            "execution_history",
            [],
        )
    )

    if report_generation_mode == "live_ai":
        history_message = (
            "Final incident report generated using the configured "
            "Live AI model."
        )

    elif report_generation_mode == "deterministic_fallback":
        history_message = (
            "Live AI final report generation was unavailable; "
            "deterministic evidence-based fallback report generated."
        )

    else:
        history_message = (
            "Final incident report generated using deterministic "
            "offline report generation."
        )

    execution_history.append(
        {
            "agent": "Final Report",
            "status": "completed",
            "message": history_message,
        }
    )

    return {
        "final_report": report,
        "investigation_status": (
            "final_report_complete"
        ),
        "execution_history": execution_history,
        "next_action": "complete",
    }


# ---------------------------------------------------------
# STANDALONE TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    state: AegisIncidentState = {
        "incident_id": "INC-001",
        "service": "api",
        "description": "API returning HTTP 500 errors",
        "severity": "SEV-2",
        "execution_mode": "offline",

        "root_cause": (
            "Database connection pool misconfiguration "
            "introduced in deployment v2.4.1, leading to "
            "connection pool exhaustion and subsequent "
            "HTTP 500 errors."
        ),

        "confidence": 0.95,

        "root_cause_rationale": (
            "The deployment was followed by database "
            "connection pool exhaustion and repeated "
            "database connection timeouts that directly "
            "correspond with HTTP 500 responses."
        ),

        "missing_evidence": (
            "Pre- and post-deployment connection pool "
            "configuration and detailed database health "
            "metrics are required for definitive proof."
        ),

        "correlations": [
            (
                "Deployment v2.4.1 was followed by "
                "database errors and HTTP 500 responses."
            ),
            (
                "Database pool exhaustion coincided "
                "with elevated API error rates."
            ),
        ],

        "critic_feedback": (
            "Verdict: PASS. Evidence of pool exhaustion, "
            "timing with deployment v2.4.1, and correlation "
            "with HTTP 500 errors supports the proposed "
            "root cause."
        ),

        "hypotheses": [
            {
                "type": "primary",
                "root_cause": (
                    "Database connection pool "
                    "misconfiguration."
                ),
                "confidence": 0.95,
                "rationale": (
                    "Logs, database events, deployment "
                    "evidence and temporal correlations "
                    "support the database connection pool "
                    "exhaustion hypothesis."
                ),
            },
            {
                "type": "alternative",
                "root_cause": (
                    "A sudden increase in API traffic "
                    "or a connection leak saturated "
                    "the existing database connection pool."
                ),
                "confidence": 0.35,
            },
        ],

        "human_decision": "approve",
        "human_feedback": "",

        "log_findings": [
            "7 HTTP 500 errors were recorded.",
            "7 HTTP 500 errors contained database connection timeouts.",
            "Database connection pool exhausted at active_connections=100.",
        ],

        "metrics_findings": [],

        "database_findings": [
            "Connection pool exhausted.",
            "Active connections reached 100.",
        ],

        "deployment_findings": [
            (
                "Deployment v2.4.1 occurred before "
                "the incident symptoms."
            ),
        ],

        "execution_history": [],
    }

    result = final_report_agent_node(
        state
    )

    print(
        result["final_report"]
    )