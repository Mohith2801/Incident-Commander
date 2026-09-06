"""
Ground-truth benchmark cases for AI Software Incident Commander.

The benchmark covers multiple incident categories so that RCA performance
can be evaluated across different failure modes rather than one scenario.
"""

BENCHMARK_CASES = [
    {
        "incident_id": "INC-001",
        "description": "API returns HTTP 500 errors and high latency after a deployment.",
        "service": "api",
        "expected_severity": "SEV-2",
        "expected_rca_category": "database_connection_pool_exhaustion",
        "expected_rca_keywords": [
            "database",
            "connection pool",
            "pool exhaustion",
            "v2.4.1",
        ],
    },
    {
        "incident_id": "INC-002",
        "description": "API errors increased immediately after a new application release.",
        "service": "api",
        "expected_severity": "SEV-2",
        "expected_rca_category": "bad_deployment",
        "expected_rca_keywords": [
            "deployment",
            "release",
            "v3.1.0",
            "rollback",
        ],
    },
    {
        "incident_id": "INC-003",
        "description": "API requests fail because the primary database is unavailable.",
        "service": "api",
        "expected_severity": "SEV-1",
        "expected_rca_category": "database_failure",
        "expected_rca_keywords": [
            "database",
            "unavailable",
            "database failure",
        ],
    },
    {
        "incident_id": "INC-004",
        "description": "API requests are timing out while an external payment service is failing.",
        "service": "api",
        "expected_severity": "SEV-2",
        "expected_rca_category": "downstream_dependency_failure",
        "expected_rca_keywords": [
            "downstream",
            "payment",
            "dependency",
            "timeout",
        ],
    },
    {
        "incident_id": "INC-005",
        "description": "API latency increased while CPU utilization reached critical levels.",
        "service": "api",
        "expected_severity": "SEV-2",
        "expected_rca_category": "cpu_resource_exhaustion",
        "expected_rca_keywords": [
            "cpu",
            "high cpu",
            "resource",
        ],
    },
    {
        "incident_id": "INC-006",
        "description": "Application instances restarted repeatedly after memory usage reached its limit.",
        "service": "api",
        "expected_severity": "SEV-1",
        "expected_rca_category": "memory_exhaustion",
        "expected_rca_keywords": [
            "memory",
            "out of memory",
            "oom",
        ],
    },
    {
        "incident_id": "INC-007",
        "description": "API requests are failing because network connectivity to the database is unstable.",
        "service": "api",
        "expected_severity": "SEV-2",
        "expected_rca_category": "network_failure",
        "expected_rca_keywords": [
            "network",
            "connectivity",
            "connection",
        ],
    },
    {
        "incident_id": "INC-008",
        "description": "Users cannot authenticate after an authentication configuration change.",
        "service": "auth",
        "expected_severity": "SEV-1",
        "expected_rca_category": "authentication_configuration_failure",
        "expected_rca_keywords": [
            "authentication",
            "configuration",
            "auth",
        ],
    },
    {
        "incident_id": "INC-009",
        "description": "API latency increased because the cache service stopped responding.",
        "service": "api",
        "expected_severity": "SEV-2",
        "expected_rca_category": "cache_failure",
        "expected_rca_keywords": [
            "cache",
            "cache service",
            "unavailable",
        ],
    },
    {
        "incident_id": "INC-010",
        "description": "Background jobs are delayed because the message queue is unavailable.",
        "service": "worker",
        "expected_severity": "SEV-2",
        "expected_rca_category": "message_queue_failure",
        "expected_rca_keywords": [
            "queue",
            "message broker",
            "message queue",
        ],
    },
]


def get_benchmark_cases():
    """Return all benchmark cases."""
    return BENCHMARK_CASES


def get_benchmark_case(incident_id):
    """Return one benchmark case by incident ID."""
    for case in BENCHMARK_CASES:
        if case["incident_id"] == incident_id:
            return case
    raise ValueError(f"Unknown benchmark incident: {incident_id}")


if __name__ == "__main__":
    print(f"Benchmark cases: {len(BENCHMARK_CASES)}")

    for case in BENCHMARK_CASES:
        print(
            f"{case['incident_id']}: "
            f"{case['expected_rca_category']} | "
            f"{case['expected_severity']}"
        )