from __future__ import annotations

from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from agents.state import AegisIncidentState
from agents.supervisor import supervisor_node
from agents.rag_agent import rag_agent_node
from agents.log_agent import log_agent_node
from agents.metrics_agent import metrics_agent_node
from agents.database_agent import database_agent_node
from agents.deployment_agent import deployment_agent_node
from agents.correlation_agent import correlation_agent_node
from agents.root_cause_agent import root_cause_agent_node
from agents.critic_agent import critic_agent_node
from agents.final_report_agent import final_report_agent_node


def add_event(
    state: AegisIncidentState,
    agent: str,
    status: str,
    message: str,
) -> list[dict]:

    history = list(
        state.get(
            "execution_history",
            [],
        )
    )

    history.append(
        {
            "agent": agent,
            "status": status,
            "message": message,
        }
    )

    return history


# ---------------------------------------------------------
# SUPERVISOR
# ---------------------------------------------------------

def supervisor_step(
    state: AegisIncidentState,
):

    result = supervisor_node(state)

    if not isinstance(result, dict):
        result = {}

    history = add_event(
        state,
        "Supervisor",
        "started",
        "Started incident investigation.",
    )

    return {
        **result,
        "execution_history": history,
        "iteration": state.get(
            "iteration",
            0,
        ),
    }


# ---------------------------------------------------------
# RAG
# ---------------------------------------------------------

def rag_step(
    state: AegisIncidentState,
):

    result = rag_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    rag_context = result.get(
        "rag_context",
        [],
    )

    history = add_event(
        state,
        "RAG",
        "completed",
        (
            f"Retrieved {len(rag_context)} "
            "relevant knowledge documents."
        ),
    )

    return {
        **result,
        "execution_history": history,
        "next_action": "analyze_logs",
    }


# ---------------------------------------------------------
# LOGS
# ---------------------------------------------------------

def log_step(
    state: AegisIncidentState,
):

    result = log_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    history = add_event(
        state,
        "Log",
        "completed",
        result.get(
            "log_agent_message",
            "Log investigation completed.",
        ),
    )

    return {
        **result,
        "execution_history": history,
    }


# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------

def metrics_step(
    state: AegisIncidentState,
):

    result = metrics_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    history = add_event(
        state,
        "Metrics",
        "completed",
        result.get(
            "metrics_agent_message",
            "Metrics investigation completed.",
        ),
    )

    return {
        **result,
        "execution_history": history,
    }


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def database_step(
    state: AegisIncidentState,
):

    result = database_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    history = add_event(
        state,
        "Database",
        "completed",
        result.get(
            "database_agent_message",
            "Database investigation completed.",
        ),
    )

    return {
        **result,
        "execution_history": history,
    }


# ---------------------------------------------------------
# DEPLOYMENT
# ---------------------------------------------------------

def deployment_step(
    state: AegisIncidentState,
):

    result = deployment_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    history = add_event(
        state,
        "Deployment",
        "completed",
        result.get(
            "deployment_agent_message",
            "Deployment investigation completed.",
        ),
    )

    return {
        **result,
        "execution_history": history,
    }


# ---------------------------------------------------------
# CORRELATION
# ---------------------------------------------------------

def correlation_step(
    state: AegisIncidentState,
):

    result = correlation_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    history = add_event(
        state,
        "Correlation",
        "completed",
        result.get(
            "correlation_agent_message",
            "Correlation analysis completed.",
        ),
    )

    return {
        **result,
        "execution_history": history,
        "next_action": "analyze_root_cause",
    }


# ---------------------------------------------------------
# ROOT CAUSE
# ---------------------------------------------------------

def root_cause_step(
    state: AegisIncidentState,
):

    result = root_cause_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    confidence = result.get(
        "confidence",
        state.get(
            "confidence",
            0.0,
        ),
    )

    try:

        confidence_value = float(
            confidence
        )

        if confidence_value > 1:
            confidence_value = (
                confidence_value / 100
            )

        confidence_value = max(
            0.0,
            min(
                1.0,
                confidence_value,
            ),
        )

    except (
        TypeError,
        ValueError,
    ):

        confidence_value = float(
            state.get(
                "confidence",
                0.0,
            )
            or 0.0
        )

    result["confidence"] = confidence_value

    confidence_text = (
        f"{confidence_value:.0%}"
    )

    message = result.get(
        "root_cause_agent_message",
        (
            "Primary root-cause hypothesis "
            f"generated with {confidence_text} confidence."
        ),
    )

    history = add_event(
        state,
        "Root Cause",
        "completed",
        str(message),
    )

    return {
        **result,
        "confidence": confidence_value,
        "execution_history": history,
        "next_action": "critic_review",
    }


# ---------------------------------------------------------
# CRITIC
# ---------------------------------------------------------

def critic_step(
    state: AegisIncidentState,
):

    result = critic_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    feedback = result.get(
        "critic_feedback",
        "Critic review completed.",
    )

    history = add_event(
        state,
        "Critic",
        "completed",
        str(feedback),
    )

    return {
        **result,
        "execution_history": history,
        "next_action": "human_review",
    }


# ---------------------------------------------------------
# CRITIC ROUTER
# ---------------------------------------------------------

def critic_router(
    state: AegisIncidentState,
) -> Literal["human_review"]:

    return "human_review"


# ---------------------------------------------------------
# HUMAN REVIEW
# ---------------------------------------------------------

def human_review_step(
    state: AegisIncidentState,
):

    root_cause = state.get(
        "root_cause",
        "No root cause generated.",
    )

    confidence = state.get(
        "confidence",
        0.0,
    )

    try:

        confidence = float(
            confidence
        )

        if confidence > 1:
            confidence = (
                confidence / 100
            )

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

    except (
        TypeError,
        ValueError,
    ):

        confidence = 0.0

    critic_feedback = state.get(
        "critic_feedback",
        "No critic feedback available.",
    )

    hypotheses = state.get(
        "hypotheses",
        [],
    )

    review_request = {
        "type": "human_review",
        "message": (
            "Please review the AI-generated "
            "root-cause analysis."
        ),
        "incident_id": state.get(
            "incident_id",
            "",
        ),
        "service": state.get(
            "service",
            "",
        ),
        "description": state.get(
            "description",
            "",
        ),
        "severity": state.get(
            "severity",
            "",
        ),
        "root_cause": root_cause,
        "confidence": confidence,
        "critic_feedback": critic_feedback,
        "hypotheses": hypotheses,
        "options": [
            "approve",
            "rework",
        ],
    }

    human_response = interrupt(
        review_request
    )

    if isinstance(
        human_response,
        dict,
    ):

        decision = str(
            human_response.get(
                "decision",
                "rework",
            )
        ).strip().lower()

        feedback = str(
            human_response.get(
                "feedback",
                "",
            )
        ).strip()

    else:

        decision = str(
            human_response
        ).strip().lower()

        feedback = ""

    if decision not in {
        "approve",
        "rework",
    }:

        decision = "rework"

    history = add_event(
        state,
        "Human",
        "completed",
        (
            f"Human decision: {decision}"
            + (
                f". Feedback: {feedback}"
                if feedback
                else "."
            )
        ),
    )

    return {
        "human_decision": decision,
        "human_feedback": feedback,
        "execution_history": history,
        "investigation_status": (
            "human_review_complete"
        ),
        "next_action": (
            "generate_final_report"
            if decision == "approve"
            else "human_rework"
        ),
    }


# ---------------------------------------------------------
# HUMAN REVIEW ROUTER
# ---------------------------------------------------------

def human_review_router(
    state: AegisIncidentState,
) -> Literal["report", "rework"]:

    decision = str(
        state.get(
            "human_decision",
            "",
        )
    ).strip().lower()

    if decision == "approve":
        return "report"

    return "rework"


# ---------------------------------------------------------
# HUMAN REQUESTED REWORK
# ---------------------------------------------------------

def human_rework_step(
    state: AegisIncidentState,
):

    iteration = (
        int(
            state.get(
                "iteration",
                0,
            )
        )
        + 1
    )

    feedback = str(
        state.get(
            "human_feedback",
            "",
        )
    ).strip()

    message = (
        "Human reviewer requested "
        "root-cause rework."
    )

    if feedback:

        message += (
            f" Feedback: {feedback}"
        )

    history = add_event(
        state,
        "Human Rework",
        "rework",
        message,
    )

    return {
        "iteration": iteration,
        "execution_history": history,
        "next_action": "analyze_root_cause",
    }


# ---------------------------------------------------------
# FINAL REPORT
# ---------------------------------------------------------

def report_step(
    state: AegisIncidentState,
):

    result = final_report_agent_node(state)

    if not isinstance(result, dict):
        result = {}

    history = result.get(
        "execution_history",
        state.get(
            "execution_history",
            [],
        ),
    )

    return {
        **result,
        "execution_history": history,
        "investigation_status": (
            "incident_report_complete"
        ),
        "next_action": "complete",
    }


# ---------------------------------------------------------
# GRAPH
# ---------------------------------------------------------

workflow = StateGraph(
    AegisIncidentState
)


# ---------------------------------------------------------
# Nodes
# ---------------------------------------------------------

workflow.add_node(
    "supervisor",
    supervisor_step,
)

workflow.add_node(
    "rag",
    rag_step,
)

workflow.add_node(
    "logs",
    log_step,
)

workflow.add_node(
    "metrics",
    metrics_step,
)

workflow.add_node(
    "database",
    database_step,
)

workflow.add_node(
    "deployment",
    deployment_step,
)

workflow.add_node(
    "correlation",
    correlation_step,
)

workflow.add_node(
    "root_cause",
    root_cause_step,
)

workflow.add_node(
    "critic",
    critic_step,
)

workflow.add_node(
    "human_review",
    human_review_step,
)

workflow.add_node(
    "human_rework",
    human_rework_step,
)

workflow.add_node(
    "report",
    report_step,
)


# ---------------------------------------------------------
# Main investigation flow
# ---------------------------------------------------------

workflow.add_edge(
    START,
    "supervisor",
)

workflow.add_edge(
    "supervisor",
    "rag",
)

workflow.add_edge(
    "rag",
    "logs",
)

workflow.add_edge(
    "logs",
    "metrics",
)

workflow.add_edge(
    "metrics",
    "database",
)

workflow.add_edge(
    "database",
    "deployment",
)

workflow.add_edge(
    "deployment",
    "correlation",
)

workflow.add_edge(
    "correlation",
    "root_cause",
)

workflow.add_edge(
    "root_cause",
    "critic",
)


# ---------------------------------------------------------
# Critic -> Human
# ---------------------------------------------------------

workflow.add_conditional_edges(
    "critic",
    critic_router,
    {
        "human_review": "human_review",
    },
)


# ---------------------------------------------------------
# Human decision
# ---------------------------------------------------------

workflow.add_conditional_edges(
    "human_review",
    human_review_router,
    {
        "report": "report",
        "rework": "human_rework",
    },
)


# ---------------------------------------------------------
# Human requested RCA rework
# ---------------------------------------------------------

workflow.add_edge(
    "human_rework",
    "root_cause",
)


# ---------------------------------------------------------
# Final report
# ---------------------------------------------------------

workflow.add_edge(
    "report",
    END,
)


# ---------------------------------------------------------
# Checkpointer
# ---------------------------------------------------------

memory = MemorySaver()

incident_graph = workflow.compile(
    checkpointer=memory,
)