from __future__ import annotations

from agents.state import AegisIncidentState
from app.rag import retrieve_incident_knowledge


def rag_agent_node(state: AegisIncidentState) -> dict:
    """Retrieve relevant knowledge from the incident knowledge base."""

    incident_id = state.get("incident_id", "")
    description = state.get("description", "")
    service = state.get("service", "")

    results = retrieve_incident_knowledge(
        incident_id=incident_id,
        description=description,
        service=service,
    )

    return {
        "rag_context": results,
        "next_action": "investigate_logs",
    }


if __name__ == "__main__":
    state: AegisIncidentState = {
        "incident_id": "INC-001",
        "description": "API returning HTTP 500 errors",
        "service": "api",
        "execution_history": [],
    }

    result = rag_agent_node(state)

    print(
        f"Retrieved documents: "
        f"{len(result.get('rag_context', []))}"
    )

    for item in result.get("rag_context", []):
        print(
            f"- {item.get('filename')} "
            f"({item.get('category')})"
        )