from __future__ import annotations

from pathlib import Path


def load_logs(
    path: str = "data/logs/application.log",
) -> list[str]:
    """
    Load application log lines from the configured log file.
    """

    file_path = Path(path)

    if not file_path.exists():
        return []

    return [
        line.strip()
        for line in file_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]


def find_error_logs(
    logs: list[str],
) -> list[str]:
    """
    Return all log entries containing ERROR.
    """

    return [
        log
        for log in logs
        if "error" in log.lower()
    ]


def find_database_errors(
    logs: list[str],
) -> list[str]:
    """
    Find log entries related to database or
    connection problems.
    """

    keywords = (
        "database",
        "connection",
        "connection pool",
        "pool exhausted",
        "timeout",
        "timed out",
    )

    return [
        log
        for log in logs
        if "error" in log.lower()
        and any(
            keyword in log.lower()
            for keyword in keywords
        )
    ]


def count_http_500_errors(
    logs: list[str],
) -> int:
    """
    Count HTTP 500 responses in application logs.
    """

    return sum(
        1
        for log in logs
        if "status=500" in log.lower()
        or "http 500" in log.lower()
        or "http/1.1\" 500" in log.lower()
    )


def find_http_500_logs(
    logs: list[str],
) -> list[str]:
    """
    Return the actual log entries containing HTTP 500 errors.
    """

    return [
        log
        for log in logs
        if (
            "status=500" in log.lower()
            or "http 500" in log.lower()
            or "http/1.1\" 500" in log.lower()
        )
    ]


if __name__ == "__main__":
    logs = load_logs()

    print(f"Log entries: {len(logs)}")
    print(
        f"Error entries: "
        f"{len(find_error_logs(logs))}"
    )
    print(
        f"Database-related errors: "
        f"{len(find_database_errors(logs))}"
    )
    print(
        f"HTTP 500 errors: "
        f"{count_http_500_errors(logs)}"
    )

    print()
    print("DATABASE ERRORS:")

    for log in find_database_errors(logs):
        print(f"- {log}")

    print()
    print("HTTP 500 LOGS:")

    for log in find_http_500_logs(logs):
        print(f"- {log}")