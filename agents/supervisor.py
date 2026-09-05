from __future__ import annotations

from agents.state import AegisIncidentState


def supervisor_node(state: AegisIncidentState) -> dict:
    """
    Supervisor starts the incident investigation.

    The supervisor sends the investigation to the RAG agent first.
    Human approval will be handled later in the workflow after
    sufficient evidence has been collected.
    """

    execution_history = list(
        state.get("execution_history", [])
    )

    execution_history.append(
        {
            "agent": "Supervisor",
            "status": "started",
            "message": "Started incident investigation.",
        }
    )

    return {
        "investigation_status": "investigation_started",
        "next_action": "retrieve_knowledge",
        "execution_history": execution_history,
    }