from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_database_events(
    path: str = "data/databases/database_events.csv",
) -> pd.DataFrame:
    """
    Load database events from CSV.
    """

    file_path = Path(path)

    if not file_path.exists():
        return pd.DataFrame()

    events = pd.read_csv(file_path)

    if events.empty:
        return events

    if "timestamp" in events.columns:
        events["timestamp"] = pd.to_datetime(
            events["timestamp"],
            errors="coerce",
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

    if "event" in events.columns:
        events["event"] = (
            events["event"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if "description" in events.columns:
        events["description"] = (
            events["description"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    if "failed_queries" in events.columns:
        events["failed_queries"] = pd.to_numeric(
            events["failed_queries"],
            errors="coerce",
        ).fillna(0)

    if "connections" in events.columns:
        events["connections"] = pd.to_numeric(
            events["connections"],
            errors="coerce",
        ).fillna(0)

    return events


def find_database_failures(
    events: pd.DataFrame,
) -> list[dict]:
    """
    Find database failure events.
    """

    if events.empty:
        return []

    failures = events[
        (
            events["event"]
            .str.lower()
            == "error"
        )
        |
        (
            events["failed_queries"]
            > 10
        )
    ]

    return failures.to_dict("records")


def find_connection_pool_exhaustion(
    events: pd.DataFrame,
) -> list[dict]:
    """
    Find events indicating database connection-pool exhaustion.
    """

    if events.empty:
        return []

    descriptions = (
        events["description"]
        .fillna("")
        .astype(str)
    )

    exhausted = events[
        descriptions.str.contains(
            "pool exhausted|connection.pool",
            case=False,
            na=False,
            regex=True,
        )
    ]

    return exhausted.to_dict("records")


def get_max_connections(
    events: pd.DataFrame,
) -> int:
    """
    Return the maximum number of database connections observed.
    """

    if events.empty:
        return 0

    if "connections" not in events.columns:
        return 0

    connections = pd.to_numeric(
        events["connections"],
        errors="coerce",
    ).dropna()

    if connections.empty:
        return 0

    return int(connections.max())


if __name__ == "__main__":
    events = load_database_events()

    print(f"Database events: {len(events)}")
    print()

    failures = find_database_failures(events)
    pool_exhaustion = find_connection_pool_exhaustion(events)
    max_connections = get_max_connections(events)

    print(f"Database failures: {len(failures)}")
    print(
        f"Connection-pool exhaustion events: "
        f"{len(pool_exhaustion)}"
    )
    print(
        f"Maximum connections: {max_connections}"
    )

    print()

    print("DATABASE FAILURES:")

    for event in failures:
        print(
            f"- {event.get('timestamp')} | "
            f"{event.get('description')}"
        )

    print()

    print("POOL EXHAUSTION:")

    for event in pool_exhaustion:
        print(
            f"- {event.get('timestamp')} | "
            f"{event.get('description')}"
        )