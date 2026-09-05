from __future__ import annotations

from agents.state import AegisIncidentState
from tools.correlation_tools import (
    correlate_database_and_metrics,
    correlate_deployments_and_failures,
)


def correlation_agent_node(
    state: AegisIncidentState,
) -> dict:
    """
    Correlate deployment, database, log, and metric evidence
    to identify relationships relevant to the incident.
    """

    deployments = state.get("deployments", [])
    database_events = state.get("database_events", [])
    logs = state.get("logs", [])
    metrics = state.get("metrics", [])

    correlations: list[str] = []

    deployment_correlations = (
        correlate_deployments_and_failures(
            deployments,
            database_events,
            logs,
        )
    )

    database_metric_correlations = (
        correlate_database_and_metrics(
            database_events,
            metrics,
        )
    )

    correlations.extend(deployment_correlations)
    correlations.extend(database_metric_correlations)

    if not correlations:
        correlations.append(
            "No strong correlation was detected between the "
            "available deployment, database, log, and metric evidence."
        )

    execution_history = list(
        state.get("execution_history", [])
    )

    execution_history.append(
        {
            "agent": "Correlation",
            "status": "completed",
            "message": (
                f"{len(correlations)} correlations identified."
            ),
        }
    )

    return {
        "correlations": correlations,
        "investigation_status": "correlation_analysis_complete",
        "execution_history": execution_history,
        "next_action": "analyze_root_cause",
    }


if __name__ == "__main__":
    state: AegisIncidentState = {
        "incident_id": "INC-001",
        "description": "API returning HTTP 500 errors",
        "service": "api",
        "deployments": [],
        "database_events": [],
        "logs": [],
        "metrics": [],
        "execution_history": [],
    }

    result = correlation_agent_node(state)

    print("CORRELATIONS:")

    for item in result.get("correlations", []):
        print(f"- {item}")

    print()
    print(
        "STATUS:",
        result.get("investigation_status"),
    )