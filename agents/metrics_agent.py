from __future__ import annotations

from agents.state import AegisIncidentState
from tools.metrics_tools import (
    calculate_baseline,
    detect_anomalies,
    load_metrics,
)


def metrics_agent_node(
    state: AegisIncidentState,
) -> dict:
    """
    Analyze service metrics and record detected anomalies.
    """

    metrics = load_metrics()

    anomalies = detect_anomalies(metrics)
    baseline = calculate_baseline(metrics)

    findings = []

    findings.append(
        f"Analyzed {len(metrics)} metric records."
    )

    if anomalies:
        findings.append(
            f"Detected {len(anomalies)} metric anomalies."
        )

    high_error_rate = [
        item
        for item in anomalies
        if item["type"] == "high_error_rate"
    ]

    high_latency = [
        item
        for item in anomalies
        if item["type"] == "high_latency"
    ]

    if high_error_rate:
        maximum = max(
            item["value"]
            for item in high_error_rate
        )

        findings.append(
            f"Error rate reached {maximum:.1f}%."
        )

    if high_latency:
        maximum = max(
            item["value"]
            for item in high_latency
        )

        findings.append(
            f"Latency reached {maximum:.0f} ms."
        )

    execution_history = list(
        state.get("execution_history", [])
    )

    execution_history.append(
        {
            "agent": "Metrics",
            "status": "completed",
            "message": (
                f"{len(metrics)} metric records analyzed. "
                + " ".join(findings)
            ),
        }
    )

    return {
        "metrics": metrics.to_dict("records"),
        "metrics_findings": findings,
        "investigation_status": "metrics_analysis_complete",
        "execution_history": execution_history,
        "next_action": "analyze_database",
    }