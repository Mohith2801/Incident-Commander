from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_metrics(
    path: str = "data/metrics/api_metrics.csv",
) -> pd.DataFrame:
    file_path = Path(path)

    if not file_path.exists():
        return pd.DataFrame()

    return pd.read_csv(file_path)


def detect_anomalies(
    metrics: pd.DataFrame,
) -> list[dict]:
    if metrics.empty:
        return []

    anomalies = []

    for _, row in metrics.iterrows():
        if row["error_rate"] > 5:
            anomalies.append(
                {
                    "timestamp": row["timestamp"],
                    "type": "high_error_rate",
                    "value": float(row["error_rate"]),
                }
            )

        if row["latency_ms"] > 500:
            anomalies.append(
                {
                    "timestamp": row["timestamp"],
                    "type": "high_latency",
                    "value": float(row["latency_ms"]),
                }
            )

    return anomalies


def calculate_baseline(
    metrics: pd.DataFrame,
) -> dict:
    if metrics.empty:
        return {}

    return {
        "average_error_rate": float(
            metrics["error_rate"].mean()
        ),
        "average_latency_ms": float(
            metrics["latency_ms"].mean()
        ),
        "average_cpu_percent": float(
            metrics["cpu_percent"].mean()
        ),
        "average_memory_percent": float(
            metrics["memory_percent"].mean()
        ),
    }