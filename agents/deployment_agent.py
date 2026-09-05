from __future__ import annotations

from agents.state import AegisIncidentState
from tools.deployment_tools import (
    find_recent_deployments,
    find_successful_deployments,
    load_deployments,
)


def deployment_agent_node(
    state: AegisIncidentState,
) -> dict:
    """
    Analyze recent deployments and identify changes
    that may be related to the incident.
    """

    deployments = load_deployments()

    service = state.get("service")

    recent_deployments = find_recent_deployments(
        deployments,
        service,
    )

    successful_deployments = (
        find_successful_deployments(deployments)
    )

    findings = [
        f"Analyzed {len(deployments)} deployment records.",
        f"Found {len(successful_deployments)} successful deployments.",
    ]

    if recent_deployments:
        latest = recent_deployments[-1]

        findings.append(
            f"Latest deployment was {latest['version']} "
            f"at {latest['timestamp']}."
        )

        findings.append(
            f"Latest deployment changes: "
            f"{latest['changes']}."
        )

    execution_history = list(
        state.get("execution_history", [])
    )

    execution_history.append(
        {
            "agent": "Deployment",
            "status": "completed",
            "message": (
                f"{len(deployments)} deployments analyzed. "
                f"Latest: "
                f"{recent_deployments[-1]['version']} "
                f"at "
                f"{recent_deployments[-1]['timestamp']}."
                if recent_deployments
                else (
                    f"{len(deployments)} deployments analyzed. "
                    "No recent deployments found."
                )
            ),
        }
    )

    return {
        "deployments": deployments.to_dict("records"),
        "deployment_findings": findings,
        "investigation_status": "deployment_analysis_complete",
        "execution_history": execution_history,
        "next_action": "correlate_evidence",
    }