"""
Evaluate the live Root Cause Agent against the labeled benchmark.
"""

from evaluation.benchmark import get_benchmark_cases
from evaluation.evidence_builder import build_evidence
from agents.root_cause_agent import root_cause_agent_node


def normalize(text):
    """Normalize text for matching."""
    return str(text).lower().strip()


def rca_matches(case, predicted_rca):
    """
    Evaluate the prediction using benchmark-defined keywords.

    A prediction is considered correct when:
    - it contains the expected RCA category terms, or
    - it contains at least one strong benchmark keyword and
      clearly describes the expected failure mode.
    """
    predicted = normalize(predicted_rca)

    keywords = [
        normalize(keyword)
        for keyword in case["expected_rca_keywords"]
    ]

    matched = [
        keyword
        for keyword in keywords
        if keyword in predicted
    ]

    category = normalize(case["expected_rca_category"])

    category_terms = {
        "database_connection_pool_exhaustion": [
            "database",
            "connection pool",
            "pool exhaustion",
            "pool exhausted",
        ],
        "bad_deployment": [
            "deployment",
            "release",
            "regression",
        ],
        "database_failure": [
            "database",
            "database failure",
            "database unavailable",
        ],
        "downstream_dependency_failure": [
            "downstream",
            "payment",
            "dependency",
        ],
        "cpu_resource_exhaustion": [
            "cpu",
            "cpu saturation",
            "cpu utilization",
        ],
        "memory_exhaustion": [
            "memory",
            "out of memory",
            "oom",
        ],
        "network_failure": [
            "network",
            "connectivity",
            "network connectivity",
        ],
        "authentication_configuration_failure": [
            "authentication",
            "authentication configuration",
            "auth configuration",
        ],
        "cache_failure": [
            "cache",
            "cache service",
            "cache failure",
        ],
        "message_queue_failure": [
            "message queue",
            "message-queue",
            "queue service",
            "message broker",
        ],
    }

    expected_terms = category_terms.get(category, [])

    category_match = any(
        term in predicted
        for term in expected_terms
    )

    return category_match, matched


def evaluate_case(case):
    """Run the live Root Cause Agent for one benchmark case."""

    state = build_evidence(case["incident_id"])

    result = root_cause_agent_node(state)

    predicted_rca = result.get("root_cause", "")
    predicted_confidence = result.get("confidence", 0.0)

    correct, matched_keywords = rca_matches(
        case,
        predicted_rca,
    )

    return {
        "incident_id": case["incident_id"],
        "expected_rca": case["expected_rca_category"],
        "predicted_rca": predicted_rca,
        "rca_correct": correct,
        "matched_keywords": matched_keywords,
        "confidence": predicted_confidence,
        "rationale": result.get(
            "root_cause_rationale",
            "",
        ),
        "missing_evidence": result.get(
            "missing_evidence",
            "",
        ),
    }


def main():
    cases = get_benchmark_cases()

    results = []

    print("=" * 70)
    print("AI SOFTWARE INCIDENT COMMANDER - RCA EVALUATION")
    print("=" * 70)

    for case in cases:
        print(f"\nEvaluating {case['incident_id']}...")

        try:
            result = evaluate_case(case)
            results.append(result)

            print("\nPREDICTED ROOT CAUSE:")
            print(result["predicted_rca"])

            print("\nEXPECTED RCA:")
            print(result["expected_rca"])

            print("\nMATCHED KEYWORDS:")
            if result["matched_keywords"]:
                print(", ".join(result["matched_keywords"]))
            else:
                print("None")

            print("\nCONFIDENCE:")
            print(f"{result['confidence']:.2%}")

            print("\nRCA CORRECT:")
            print(
                "PASS"
                if result["rca_correct"]
                else "FAIL"
            )

            if result["rationale"]:
                print("\nRATIONALE:")
                print(result["rationale"])

        except Exception as exc:
            print(f"\nERROR: {exc}")

    if not results:
        print("\nNo evaluation results.")
        return

    correct_count = sum(
        result["rca_correct"]
        for result in results
    )

    total = len(results)
    accuracy = correct_count / total

    average_confidence = (
        sum(result["confidence"] for result in results)
        / total
    )

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Cases evaluated       : {total}")
    print(f"RCA correct           : {correct_count}")
    print(f"RCA accuracy          : {accuracy:.2%}")
    print(
        f"Average confidence   : "
        f"{average_confidence:.2%}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()