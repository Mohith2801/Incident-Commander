from __future__ import annotations

from datetime import datetime


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(
        str(value),
        "%Y-%m-%d %H:%M:%S",
    )


def parse_log_timestamp(message: str) -> datetime | None:
    try:
        parts = message.split(" ", 2)

        if len(parts) < 2:
            return None

        return datetime.strptime(
            f"{parts[0]} {parts[1]}",
            "%Y-%m-%d %H:%M:%S",
        )

    except (ValueError, IndexError):
        return None


def correlate_deployments_and_failures(
    deployments: list[dict],
    database_events: list[dict],
    logs: list[dict],
) -> list[str]:

    correlations = []

    for deployment in deployments:

        if deployment.get("status", "").lower() != "success":
            continue

        deployment_time = parse_timestamp(
            deployment["timestamp"]
        )

        for event in database_events:

            event_time = parse_timestamp(
                event["timestamp"]
            )

            difference = (
                event_time - deployment_time
            ).total_seconds() / 60

            if 0 <= difference <= 30:

                if event.get("event") == "error":

                    correlations.append(
                        f"Deployment {deployment['version']} "
                        f"occurred {difference:.0f} minutes before "
                        f"a database error."
                    )

        for log in logs:

            message = log.get("message", "")

            if "status=500" not in message:
                continue

            log_time = parse_log_timestamp(message)

            if log_time is None:
                continue

            difference = (
                log_time - deployment_time
            ).total_seconds() / 60

            if 0 <= difference <= 30:

                correlations.append(
                    f"Deployment {deployment['version']} "
                    f"occurred {difference:.0f} minutes before "
                    f"an HTTP 500 error."
                )

    return correlations


def correlate_database_and_metrics(
    database_events: list[dict],
    metrics: list[dict],
) -> list[str]:

    correlations = []

    database_by_time = {
        str(event["timestamp"]): event
        for event in database_events
    }

    for metric in metrics:

        timestamp = str(metric["timestamp"])

        database_event = database_by_time.get(timestamp)

        if not database_event:
            continue

        if database_event.get("event") != "error":
            continue

        error_rate = float(
            metric.get("error_rate", 0)
        )

        latency = float(
            metric.get("latency_ms", 0)
        )

        if error_rate > 5:

            correlations.append(
                f"At {timestamp}, database errors coincided "
                f"with an error rate of {error_rate:.1f}%."
            )

        if latency > 500:

            correlations.append(
                f"At {timestamp}, database errors coincided "
                f"with latency of {latency:.0f} ms."
            )

    return correlations