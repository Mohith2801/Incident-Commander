"""
Build controlled evidence states for RCA benchmark cases.

The evidence in this module is synthetic evaluation data.
It is intentionally separate from the production investigation tools.
"""

from evaluation.benchmark import get_benchmark_case


def build_evidence(case_id):
    """Return evidence appropriate for a benchmark incident."""

    case = get_benchmark_case(case_id)

    builders = {
        "INC-001": _inc_001,
        "INC-002": _inc_002,
        "INC-003": _inc_003,
        "INC-004": _inc_004,
        "INC-005": _inc_005,
        "INC-006": _inc_006,
        "INC-007": _inc_007,
        "INC-008": _inc_008,
        "INC-009": _inc_009,
        "INC-010": _inc_010,
    }

    builder = builders.get(case_id)

    if builder is None:
        raise ValueError(
            f"No evidence builder for {case_id}"
        )

    return builder(case)


def _base_evidence(case):
    """Create the common benchmark state fields."""

    return {
        "incident_id": case["incident_id"],
        "description": case["description"],
        "service": case["service"],
        "severity": case["expected_severity"],
        "logs": [],
        "metrics": [],
        "database_events": [],
        "deployments": [],
        "log_findings": [],
        "metrics_findings": [],
        "database_findings": [],
        "deployment_findings": [],
        "correlations": [],
        "rag_context": [],
        "human_feedback": "",
    }


def _inc_001(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "http_500_count": 8,
            "database_errors": 6,
            "pool_exhaustion": True,
        }
    ]

    state["metrics_findings"] = [
        {
            "max_error_rate": 15.8,
            "max_latency_ms": 1100,
        }
    ]

    state["database_findings"] = [
        {
            "failure_count": 8,
            "max_connections": 100,
            "pool_exhaustion": True,
        }
    ]

    state["deployment_findings"] = [
        {
            "latest_deployment": "v2.4.1",
            "deployment_change": (
                "Database connection pool configuration"
            ),
        }
    ]

    state["correlations"] = [
        {
            "type": "deployment_database_failure",
            "description": (
                "Deployment v2.4.1 preceded database "
                "connection failures and pool exhaustion."
            ),
        },
        {
            "type": "database_metrics",
            "description": (
                "Database connection failures correlate "
                "with elevated error rate and latency."
            ),
        },
    ]

    return state


def _inc_002(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "http_500_count": 42,
            "application_errors": 38,
        }
    ]

    state["metrics_findings"] = [
        {
            "error_rate_before_release": 0.8,
            "error_rate_after_release": 18.4,
            "latency_before_release": 210,
            "latency_after_release": 940,
        }
    ]

    state["deployment_findings"] = [
        {
            "latest_deployment": "v3.1.0",
            "deployment_change": "New application release",
            "status": "success",
        }
    ]

    state["correlations"] = [
        {
            "type": "deployment_application_failure",
            "description": (
                "Application errors increased immediately "
                "after deployment v3.1.0."
            ),
        }
    ]

    return state


def _inc_003(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "http_500_count": 55,
            "database_unavailable_errors": 31,
        }
    ]

    state["database_findings"] = [
        {
            "failure_count": 31,
            "database_status": "unavailable",
            "failure_type": "database failure",
        }
    ]

    state["metrics_findings"] = [
        {
            "max_error_rate": 32.5,
            "max_latency_ms": 1250,
        }
    ]

    state["correlations"] = [
        {
            "type": "database_outage",
            "description": (
                "Database became unavailable at the same "
                "time API failures increased."
            ),
        }
    ]

    return state


def _inc_004(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "timeout_count": 27,
            "payment_service_errors": 24,
        }
    ]

    state["metrics_findings"] = [
        {
            "max_error_rate": 14.2,
            "max_latency_ms": 1800,
        }
    ]

    state["database_findings"] = [
        {
            "database_status": "healthy",
            "failure_count": 0,
        }
    ]

    state["correlations"] = [
        {
            "type": "downstream_dependency",
            "description": (
                "Payment dependency failures coincided "
                "with API timeouts."
            ),
        }
    ]

    return state


def _inc_005(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "slow_request_count": 36,
            "resource_warning": "high CPU",
        }
    ]

    state["metrics_findings"] = [
        {
            "max_cpu_percent": 98.7,
            "max_error_rate": 8.4,
            "max_latency_ms": 1350,
        }
    ]

    state["database_findings"] = [
        {
            "database_status": "healthy",
            "failure_count": 0,
        }
    ]

    state["correlations"] = [
        {
            "type": "cpu_resource",
            "description": (
                "API latency increased as CPU utilization "
                "reached critical levels."
            ),
        }
    ]

    return state


def _inc_006(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "restart_count": 17,
            "memory_errors": 12,
            "oom_events": 8,
        }
    ]

    state["metrics_findings"] = [
        {
            "max_memory_percent": 99.6,
            "max_error_rate": 21.3,
        }
    ]

    state["correlations"] = [
        {
            "type": "memory_exhaustion",
            "description": (
                "Application restarts occurred after memory "
                "usage reached its limit."
            ),
        }
    ]

    return state


def _inc_007(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "database_connection_errors": 29,
            "network_errors": 24,
        }
    ]

    state["database_findings"] = [
        {
            "database_status": "reachable intermittently",
            "failure_count": 24,
            "failure_type": "network connectivity",
        }
    ]

    state["metrics_findings"] = [
        {
            "max_error_rate": 16.1,
            "max_latency_ms": 1420,
        }
    ]

    state["correlations"] = [
        {
            "type": "network_database",
            "description": (
                "Database connection failures coincided "
                "with unstable network connectivity."
            ),
        }
    ]

    return state


def _inc_008(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "authentication_failures": 74,
            "auth_error_type": "invalid configuration",
        }
    ]

    state["deployment_findings"] = [
        {
            "configuration_change": "Authentication configuration",
            "status": "success",
        }
    ]

    state["metrics_findings"] = [
        {
            "authentication_failure_rate": 96.2,
        }
    ]

    state["correlations"] = [
        {
            "type": "authentication_configuration",
            "description": (
                "Authentication failures increased immediately "
                "after an authentication configuration change."
            ),
        }
    ]

    return state


def _inc_009(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "cache_errors": 41,
            "cache_service_status": "unavailable",
        }
    ]

    state["metrics_findings"] = [
        {
            "max_latency_ms": 1600,
            "max_error_rate": 11.7,
        }
    ]

    state["correlations"] = [
        {
            "type": "cache_failure",
            "description": (
                "API latency increased after the cache service "
                "stopped responding."
            ),
        }
    ]

    return state


def _inc_010(case):
    state = _base_evidence(case)

    state["log_findings"] = [
        {
            "delayed_jobs": 63,
            "queue_errors": 35,
            "message_queue_status": "unavailable",
        }
    ]

    state["metrics_findings"] = [
        {
            "queue_depth": 18420,
            "job_delay_minutes": 47,
        }
    ]

    state["correlations"] = [
        {
            "type": "message_queue_failure",
            "description": (
                "Background job delays increased while the "
                "message queue was unavailable."
            ),
        }
    ]

    return state


if __name__ == "__main__":
    for case_id in [
        "INC-001",
        "INC-002",
        "INC-003",
        "INC-004",
        "INC-005",
        "INC-006",
        "INC-007",
        "INC-008",
        "INC-009",
        "INC-010",
    ]:
        evidence = build_evidence(case_id)

        print(
            f"{case_id}: "
            f"{len(evidence['log_findings'])} log findings, "
            f"{len(evidence['metrics_findings'])} metric findings, "
            f"{len(evidence['database_findings'])} database findings, "
            f"{len(evidence['deployment_findings'])} deployment findings, "
            f"{len(evidence['correlations'])} correlations"
        )