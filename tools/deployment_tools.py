from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_deployments(
    path: str = "data/deployments/deployment_history.csv",
) -> pd.DataFrame:
    """
    Load deployment history from CSV.
    """

    file_path = Path(path)

    if not file_path.exists():
        return pd.DataFrame()

    deployments = pd.read_csv(file_path)

    if deployments.empty:
        return deployments

    if "timestamp" in deployments.columns:
        deployments["timestamp"] = pd.to_datetime(
            deployments["timestamp"],
            errors="coerce",
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

    if "status" in deployments.columns:
        deployments["status"] = (
            deployments["status"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if "service" in deployments.columns:
        deployments["service"] = (
            deployments["service"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if "version" in deployments.columns:
        deployments["version"] = (
            deployments["version"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return deployments


def find_recent_deployments(
    deployments: pd.DataFrame,
    service: str | None = None,
) -> list[dict]:
    """
    Return the five most recent deployments,
    optionally filtered by service.
    """

    if deployments.empty:
        return []

    result = deployments.copy()

    if service and "service" in result.columns:
        result = result[
            result["service"].str.lower()
            == service.strip().lower()
        ]

    if "timestamp" in result.columns:
        result = result.sort_values("timestamp")

    return result.tail(5).to_dict("records")


def find_successful_deployments(
    deployments: pd.DataFrame,
) -> list[dict]:
    """
    Return all successful deployments.
    """

    if deployments.empty:
        return []

    if "status" not in deployments.columns:
        return []

    result = deployments[
        deployments["status"].str.lower() == "success"
    ]

    return result.to_dict("records")


if __name__ == "__main__":
    deployments = load_deployments()

    print(f"Deployment records: {len(deployments)}")
    print()

    if not deployments.empty:
        print(deployments.to_string(index=False))

        print()
        print("SUCCESSFUL DEPLOYMENTS:")

        successful = find_successful_deployments(
            deployments
        )

        for deployment in successful:
            print(
                f"- {deployment.get('version')} "
                f"| {deployment.get('timestamp')} "
                f"| {deployment.get('service')} "
                f"| {deployment.get('status')}"
            )