from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

import app.graph as graph_module


# ---------------------------------------------------------
# OFFLINE TEST STUBS
# ---------------------------------------------------------
# These replace all LLM-dependent steps.
# The real graph routing, human interrupt, checkpointing,
# human rework and final report logic are still tested.
# ---------------------------------------------------------


def fake_rag_step(state):
    return {
        "rag_context": [
            {
                "filename": "http_500_database_errors.md",
                "category": "runbook",
                "content": (
                    "HTTP 500 errors can occur when database "
                    "connection pools are exhausted."
                ),
            }
        ],
        "investigation_status": "rag_complete",
        "next_action": "analyze_logs",
        "execution_history": graph_module.add_event(
            state,
            "RAG",
            "completed",
            "Retrieved offline knowledge document.",
        ),
    }


def fake_root_cause_step(state):
    feedback = str(
        state.get("human_feedback", "")
    ).strip()

    iteration = int(
        state.get("iteration", 0)
    )

    root_cause = (
        "Database connection pool misconfiguration introduced "
        "in deployment v2.4.1 caused connection pool exhaustion "
        "and subsequent HTTP 500 errors."
    )

    if feedback:
        rationale = (
            "The RCA was revised using human review feedback "
            "while preserving the evidence-supported database "
            "connection pool hypothesis."
        )
        message = (
            "Offline RCA was revised using human feedback."
        )
    else:
        rationale = (
            "Logs, database events, deployment evidence and "
            "temporal correlations support the database "
            "connection pool exhaustion hypothesis."
        )
        message = (
            "Offline RCA generated successfully."
        )

    alternative = (
        "A downstream database dependency failure may have "
        "independently contributed to the HTTP 500 errors."
    )

    history = graph_module.add_event(
        state,
        "Root Cause",
        "completed",
        message,
    )

    return {
        "root_cause": root_cause,
        "confidence": 0.95,
        "hypotheses": [
            {
                "type": "primary",
                "root_cause": root_cause,
                "confidence": 0.95,
                "rationale": rationale,
                "missing_evidence": (
                    "Database connection pool configuration "
                    "and deployment configuration should be "
                    "verified in production."
                ),
            },
            {
                "type": "alternative",
                "root_cause": alternative,
                "confidence": 0.25,
            },
        ],
        "root_cause_rationale": rationale,
        "missing_evidence": (
            "Verify production connection pool configuration."
        ),
        "root_cause_agent_message": message,
        "investigation_status": (
            "root_cause_analysis_complete"
        ),
        "next_action": "critic_review",
        "iteration": iteration,
        "execution_history": history,
    }


def fake_critic_step(state):
    feedback = (
        "Verdict: PASS. The root cause is supported by "
        "multiple independent evidence sources."
    )

    history = graph_module.add_event(
        state,
        "Critic",
        "completed",
        feedback,
    )

    return {
        "critic_feedback": feedback,
        "investigation_status": "critic_review_complete",
        "next_action": "human_review",
        "execution_history": history,
    }


# ---------------------------------------------------------
# BUILD A REAL OFFLINE GRAPH
# ---------------------------------------------------------
# IMPORTANT:
#
# We do NOT modify graph_module.workflow after it has
# already been constructed.
#
# Instead, we construct a fresh graph and explicitly insert
# the offline functions.
#
# This guarantees that no Groq-dependent RCA or critic
# function can accidentally execute.
# ---------------------------------------------------------


offline_workflow = StateGraph(
    graph_module.AegisIncidentState
)


# ---------------------------------------------------------
# REAL NON-LLM NODES
# ---------------------------------------------------------

offline_workflow.add_node(
    "supervisor",
    graph_module.supervisor_step,
)

offline_workflow.add_node(
    "logs",
    graph_module.log_step,
)

offline_workflow.add_node(
    "metrics",
    graph_module.metrics_step,
)

offline_workflow.add_node(
    "database",
    graph_module.database_step,
)

offline_workflow.add_node(
    "deployment",
    graph_module.deployment_step,
)

offline_workflow.add_node(
    "correlation",
    graph_module.correlation_step,
)

# Offline replacements for LLM-dependent nodes.
offline_workflow.add_node(
    "rag",
    fake_rag_step,
)

offline_workflow.add_node(
    "root_cause",
    fake_root_cause_step,
)

offline_workflow.add_node(
    "critic",
    fake_critic_step,
)

# Real human-review and final-report logic.
offline_workflow.add_node(
    "human_review",
    graph_module.human_review_step,
)

offline_workflow.add_node(
    "human_rework",
    graph_module.human_rework_step,
)

offline_workflow.add_node(
    "report",
    graph_module.report_step,
)


# ---------------------------------------------------------
# MAIN INVESTIGATION FLOW
# ---------------------------------------------------------

offline_workflow.add_edge(
    START,
    "supervisor",
)

offline_workflow.add_edge(
    "supervisor",
    "rag",
)

offline_workflow.add_edge(
    "rag",
    "logs",
)

offline_workflow.add_edge(
    "logs",
    "metrics",
)

offline_workflow.add_edge(
    "metrics",
    "database",
)

offline_workflow.add_edge(
    "database",
    "deployment",
)

offline_workflow.add_edge(
    "deployment",
    "correlation",
)

offline_workflow.add_edge(
    "correlation",
    "root_cause",
)

offline_workflow.add_edge(
    "root_cause",
    "critic",
)


# ---------------------------------------------------------
# CRITIC -> HUMAN REVIEW
# ---------------------------------------------------------

offline_workflow.add_conditional_edges(
    "critic",
    graph_module.critic_router,
    {
        "human_review": "human_review",
    },
)


# ---------------------------------------------------------
# HUMAN REVIEW ROUTING
# ---------------------------------------------------------

offline_workflow.add_conditional_edges(
    "human_review",
    graph_module.human_review_router,
    {
        "report": "report",
        "rework": "human_rework",
    },
)


# ---------------------------------------------------------
# HUMAN REWORK -> RCA
# ---------------------------------------------------------

offline_workflow.add_edge(
    "human_rework",
    "root_cause",
)


# ---------------------------------------------------------
# FINAL REPORT -> END
# ---------------------------------------------------------

offline_workflow.add_edge(
    "report",
    END,
)


# ---------------------------------------------------------
# OFFLINE CHECKPOINTER
# ---------------------------------------------------------

offline_memory = MemorySaver()

offline_graph = offline_workflow.compile(
    checkpointer=offline_memory,
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


def print_history(history):
    print()
    print("AGENT EXECUTION:")
    print()

    for i, event in enumerate(history, 1):
        print(
            f"{i}. {event.get('agent', 'Unknown')} "
            f"[{event.get('status', 'unknown')}]"
        )

        print(
            f"   {event.get('message', '')}"
        )


def assert_condition(
    condition: bool,
    message: str,
):
    if not condition:
        raise AssertionError(message)

    print(f"[PASS] {message}")


# ---------------------------------------------------------
# INITIAL INCIDENT
# ---------------------------------------------------------

initial_state = {
    "incident_id": "INC-001",
    "description": "API returning HTTP 500 errors",
    "service": "api",
    "severity": "SEV-2",
    "iteration": 0,
    "execution_history": [],
    "logs": [],
    "metrics": [],
    "database_events": [],
    "deployments": [],
    "log_findings": [
        "Found 9 error log entries.",
        "Found 7 HTTP 500 errors.",
        "Database-related errors were detected.",
        "Database connection pool exhaustion was detected.",
    ],
    "metrics_findings": [
        "Analyzed 16 metric records.",
        "Detected metric anomalies.",
        "Error rate increased during the incident.",
        "Latency increased during the incident.",
    ],
    "database_findings": [
        "Analyzed database events.",
        "Database failure events were detected.",
        "Maximum database connections reached the configured limit.",
        "Database connection pool exhaustion was detected.",
    ],
    "deployment_findings": [
        "Analyzed deployment records.",
        "Found successful deployments.",
        "Latest deployment was v2.4.1.",
        "Latest deployment introduced database-related changes.",
    ],
    "correlations": [
        "Deployment v2.4.1 occurred shortly before a database error.",
        "Deployment v2.4.1 occurred shortly before HTTP 500 errors.",
        "Database errors coincided with an elevated error rate.",
        "Database errors coincided with increased latency.",
    ],
}


# ---------------------------------------------------------
# TEST 1 - GRAPH STARTUP
# ---------------------------------------------------------

print("========================================")
print("       OFFLINE GRAPH TEST")
print("========================================")
print()

print(
    "Starting offline incident investigation..."
)

print(
    "Groq API will NOT be called."
)

print()


config = {
    "configurable": {
        "thread_id": "OFFLINE-INC-001"
    }
}


result = offline_graph.invoke(
    initial_state,
    config=config,
)


# ---------------------------------------------------------
# TEST 2 - HUMAN REVIEW INTERRUPT
# ---------------------------------------------------------

assert_condition(
    "__interrupt__" in result,
    "Graph paused for human review.",
)


interrupt = result["__interrupt__"][0]
interrupt_data = interrupt.value


print()
print("========================================")
print("       HUMAN REVIEW REQUIRED")
print("========================================")
print()

print(
    interrupt_data.get(
        "message",
        "Please review the investigation.",
    )
)

print()
print("Incident ID:")
print(
    interrupt_data.get(
        "incident_id",
        initial_state["incident_id"],
    )
)

print()
print("Service:")
print(
    interrupt_data.get(
        "service",
        initial_state["service"],
    )
)

print()
print("Root Cause:")
print(
    interrupt_data.get(
        "root_cause",
        result.get(
            "root_cause",
            "Unknown",
        ),
    )
)

print()
print("Confidence:")
print(
    interrupt_data.get(
        "confidence",
        result.get(
            "confidence",
            0.0,
        ),
    )
)

print()
print("Critic Feedback:")
print(
    interrupt_data.get(
        "critic_feedback",
        result.get(
            "critic_feedback",
            "No critic feedback.",
        ),
    )
)


# ---------------------------------------------------------
# TEST 3 - HUMAN APPROVAL
# ---------------------------------------------------------

print()
print("----------------------------------------")
print("Testing HUMAN APPROVE path...")
print("----------------------------------------")
print()


result = offline_graph.invoke(
    Command(
        resume={
            "decision": "approve",
            "feedback": "",
        }
    ),
    config=config,
)


# ---------------------------------------------------------
# TEST 4 - FINAL REPORT
# ---------------------------------------------------------

assert_condition(
    "__interrupt__" not in result,
    "Graph continued after human approval.",
)

assert_condition(
    result.get("human_decision") == "approve",
    "Human approval was stored in graph state.",
)

assert_condition(
    result.get("investigation_status")
    == "incident_report_complete",
    "Final report was generated.",
)

assert_condition(
    bool(result.get("final_report")),
    "Final report contains content.",
)

assert_condition(
    result.get("next_action") == "complete",
    "Graph reached the complete state.",
)

assert_condition(
    "root_cause" in result,
    "Root cause is present in final state.",
)

assert_condition(
    result.get("confidence", 0) > 0,
    "Root-cause confidence is greater than zero.",
)


# ---------------------------------------------------------
# PRINT APPROVAL RESULT
# ---------------------------------------------------------

print()
print("========================================")
print("       APPROVAL TEST RESULT")
print("========================================")
print()

print(
    "STATUS:",
    result.get(
        "investigation_status",
        "unknown",
    ),
)

print()
print("ROOT CAUSE:")
print(
    result.get(
        "root_cause",
        "Not available.",
    )
)

print()
print("CONFIDENCE:")
print(
    result.get(
        "confidence",
        0.0,
    )
)

print()
print("HUMAN DECISION:")
print(
    result.get(
        "human_decision",
        "Not available.",
    )
)

print()
print("FINAL REPORT:")
print(
    result.get(
        "final_report",
        "Report not generated.",
    )
)

print_history(
    result.get(
        "execution_history",
        [],
    )
)


# ---------------------------------------------------------
# TEST 5 - HUMAN REWORK PATH
# ---------------------------------------------------------

print()
print("========================================")
print("       HUMAN REWORK TEST")
print("========================================")
print()


rework_config = {
    "configurable": {
        "thread_id": "OFFLINE-INC-002"
    }
}


rework_result = offline_graph.invoke(
    initial_state,
    config=rework_config,
)


assert_condition(
    "__interrupt__" in rework_result,
    "Second investigation paused for human review.",
)


# ---------------------------------------------------------
# TEST 6 - RESUME WITH REWORK
# ---------------------------------------------------------

human_feedback = (
    "Re-evaluate whether the deployment change directly "
    "caused the connection pool exhaustion and clearly "
    "identify the evidence that should be verified."
)


rework_result = offline_graph.invoke(
    Command(
        resume={
            "decision": "rework",
            "feedback": human_feedback,
        }
    ),
    config=rework_config,
)


# The human_rework node sends the workflow back to RCA.
# The revised RCA then goes through critic and human review.


assert_condition(
    "__interrupt__" in rework_result,
    "Graph returned to human review after RCA rework.",
)

assert_condition(
    rework_result.get("human_decision")
    == "rework",
    "Human rework decision was stored.",
)

assert_condition(
    rework_result.get("human_feedback")
    == human_feedback,
    "Human feedback was stored in graph state.",
)

assert_condition(
    rework_result.get("iteration", 0) >= 1,
    "RCA iteration count increased after rework.",
)

assert_condition(
    "Human Rework" in str(
        rework_result.get(
            "execution_history",
            [],
        )
    ),
    "Human rework was recorded in execution history.",
)


# ---------------------------------------------------------
# TEST 7 - APPROVE REVISED RCA
# ---------------------------------------------------------

print()
print("----------------------------------------")
print("Approving revised RCA...")
print("----------------------------------------")
print()


rework_result = offline_graph.invoke(
    Command(
        resume={
            "decision": "approve",
            "feedback": "",
        }
    ),
    config=rework_config,
)


assert_condition(
    "__interrupt__" not in rework_result,
    "Reworked investigation completed after approval.",
)

assert_condition(
    rework_result.get("human_decision")
    == "approve",
    "Final human decision is approve.",
)

assert_condition(
    rework_result.get("investigation_status")
    == "incident_report_complete",
    "Final report generated after rework.",
)

assert_condition(
    bool(
        rework_result.get(
            "final_report"
        )
    ),
    "Reworked final report contains content.",
)


# ---------------------------------------------------------
# FINAL OUTPUT
# ---------------------------------------------------------

print()
print("========================================")
print("       REWORK TEST RESULT")
print("========================================")
print()

print(
    "STATUS:",
    rework_result.get(
        "investigation_status",
        "unknown",
    ),
)

print()
print("ITERATION:")
print(
    rework_result.get(
        "iteration",
        0,
    )
)

print()
print("ROOT CAUSE:")
print(
    rework_result.get(
        "root_cause",
        "Not available.",
    )
)

print()
print("CONFIDENCE:")
print(
    rework_result.get(
        "confidence",
        0.0,
    )
)

print()
print("HUMAN DECISION:")
print(
    rework_result.get(
        "human_decision",
        "Not available.",
    )
)

print()
print("HUMAN FEEDBACK:")
print(
    rework_result.get(
        "human_feedback",
        "None.",
    )
)

print()
print("FINAL REPORT:")
print(
    rework_result.get(
        "final_report",
        "Report not generated.",
    )
)

print_history(
    rework_result.get(
        "execution_history",
        [],
    )
)


# ---------------------------------------------------------
# FINAL SUCCESS
# ---------------------------------------------------------

print()
print("========================================")
print("       ALL OFFLINE TESTS PASSED")
print("========================================")
print()

print("Graph compilation       : PASS")
print("Human interrupt         : PASS")
print("Human approval          : PASS")
print("Final report            : PASS")
print("Human rework            : PASS")
print("Feedback persistence    : PASS")
print("Iteration handling      : PASS")
print("Reworked RCA            : PASS")
print("Graph completion        : PASS")
print()
print("Groq API calls          : 0")
print()
print("GRAPH OFFLINE TEST OK")
print("========================================")