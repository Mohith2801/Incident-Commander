from __future__ import annotations

from agents.state import AegisIncidentState
from tools.database_tools import (
    find_connection_pool_exhaustion,
    find_database_failures,
    get_max_connections,
    load_database_events,
)


def database_agent_node(
    state: AegisIncidentState,
) -> dict:
    """
    Analyze database events, failures, and connection-pool usage.
    """

    events = load_database_events()

    failures = find_database_failures(events)
    pool_exhaustion = find_connection_pool_exhaustion(events)
    max_connections = get_max_connections(events)

    findings = [
        f"Analyzed {len(events)} database events.",
        f"Detected {len(failures)} database failure events.",
        f"Maximum database connections reached {max_connections}.",
    ]

    if pool_exhaustion:
        findings.append(
            "Database connection pool exhaustion was detected."
        )

    execution_history = list(
        state.get("execution_history", [])
    )

    execution_history.append(
        {
            "agent": "Database",
            "status": "completed",
            "message": (
                f"{len(events)} database events analyzed. "
                f"{len(failures)} failures detected. "
                f"Maximum connections: {max_connections}."
            ),
        }
    )

    return {
        "database_events": events.to_dict("records"),
        "database_findings": findings,
        "investigation_status": "database_analysis_complete",
        "execution_history": execution_history,
        "next_action": "analyze_deployments",
    }