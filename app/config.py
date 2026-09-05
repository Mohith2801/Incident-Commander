from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # ============================================================
    # APPLICATION
    # ============================================================
    app_env: str = os.getenv(
        "APP_ENV",
        "development",
    )

    log_level: str = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )

    # ============================================================
    # LLM CONFIGURATION
    # ============================================================
    llm_provider: str = os.getenv(
        "LLM_PROVIDER",
        "groq",
    )

    llm_model: str = os.getenv(
        "LLM_MODEL",
        "openai/gpt-oss-120b",
    )

    # ============================================================
    # GROQ API
    # ============================================================
    groq_api_key: str = os.getenv(
        "GROQ_API_KEY",
        "",
    )

    # ============================================================
    # INCIDENT INVESTIGATION
    # ============================================================
    max_evidence_items: int = int(
        os.getenv(
            "MAX_EVIDENCE_ITEMS",
            "20",
        )
    )

    confidence_threshold: float = float(
        os.getenv(
            "CONFIDENCE_THRESHOLD",
            "0.70",
        )
    )

    # Maximum number of root-cause investigation iterations.
    max_iterations: int = int(
        os.getenv(
            "MAX_ITERATIONS",
            "2",
        )
    )

    # ============================================================
    # RAG CONFIGURATION
    # ============================================================
    rag_enabled: bool = (
        os.getenv(
            "RAG_ENABLED",
            "true",
        ).lower()
        == "true"
    )

    rag_top_k: int = int(
        os.getenv(
            "RAG_TOP_K",
            "3",
        )
    )

    knowledge_dir: str = os.getenv(
        "KNOWLEDGE_DIR",
        "knowledge",
    )

    # ============================================================
    # HUMAN-IN-THE-LOOP CONFIGURATION
    # ============================================================
    hitl_enabled: bool = (
        os.getenv(
            "HITL_ENABLED",
            "true",
        ).lower()
        == "true"
    )

    # Require human review when the critic requests rework
    # or when confidence is below the configured threshold.
    hitl_require_on_rework: bool = (
        os.getenv(
            "HITL_REQUIRE_ON_REWORK",
            "true",
        ).lower()
        == "true"
    )

    hitl_confidence_threshold: float = float(
        os.getenv(
            "HITL_CONFIDENCE_THRESHOLD",
            "0.80",
        )
    )

    # ============================================================
    # DATA DIRECTORIES
    # ============================================================
    data_dir: str = os.getenv(
        "DATA_DIR",
        "data",
    )

    incidents_dir: str = os.getenv(
        "INCIDENTS_DIR",
        "data/incidents",
    )

    logs_dir: str = os.getenv(
        "LOGS_DIR",
        "data/logs",
    )

    metrics_dir: str = os.getenv(
        "METRICS_DIR",
        "data/metrics",
    )

    deployments_dir: str = os.getenv(
        "DEPLOYMENTS_DIR",
        "data/deployments",
    )

    databases_dir: str = os.getenv(
        "DATABASES_DIR",
        "data/databases",
    )


settings = Settings()