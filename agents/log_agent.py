from __future__ import annotations

from agents.state import AegisIncidentState
from tools.log_tools import (
    count_http_500_errors,
    find_database_errors,
    find_error_logs,
    load_logs,
)


def log_agent_node(
    state: AegisIncidentState,
) -> dict:
    """
    Analyze application logs and record the findings.
    """

    logs = load_logs()

    error_logs = find_error_logs(logs)
    database_errors = find_database_errors(logs)
    http_500_count = count_http_500_errors(logs)

    findings = [
        f"Found {len(error_logs)} error log entries.",
        f"Found {http_500_count} HTTP 500 errors.",
    ]

    if database_errors:
        findings.append(
            "Database-related errors were detected."
        )

    if any(
        "connection pool exhausted" in log.lower()
        for log in database_errors
    ):
        findings.append(
            "Database connection pool exhaustion was detected."
        )

    execution_history = list(
        state.get("execution_history", [])
    )

    execution_history.append(
        {
            "agent": "Log",
            "status": "completed",
            "message": (
                f"{len(error_logs)} error logs found, "
                f"{http_500_count} HTTP 500 errors. "
                + " ".join(findings)
            ),
        }
    )

    return {
        "logs": [{"message": log} for log in logs],
        "log_findings": findings,
        "investigation_status": "log_analysis_complete",
        "execution_history": execution_history,
        "next_action": "analyze_metrics",
    }