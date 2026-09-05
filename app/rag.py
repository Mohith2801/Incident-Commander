from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from app.config import settings


def get_knowledge_dir() -> Path:
    """Return the configured knowledge-base directory."""
    return Path(settings.knowledge_dir)


def load_knowledge_documents() -> list[Document]:
    """Load all Markdown documents from the knowledge base."""
    documents: list[Document] = []
    knowledge_dir = get_knowledge_dir()

    if not knowledge_dir.exists():
        return documents

    for path in sorted(knowledge_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")

        if not text.strip():
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(path),
                    "filename": path.name,
                    "category": path.parent.name,
                },
            )
        )

    return documents


def build_vector_store(
    documents: list[Document] | None = None,
) -> InMemoryVectorStore:
    """Build an in-memory vector store from knowledge documents."""

    if documents is None:
        documents = load_knowledge_documents()

    vector_store = InMemoryVectorStore(
        embedding=FakeEmbeddings(size=384)
    )

    if documents:
        vector_store.add_documents(documents)

    return vector_store


def retrieve_knowledge(
    query: str,
    k: int | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve knowledge documents relevant to a query.

    Returns document content together with source metadata.
    """

    if not query.strip():
        return []

    documents = load_knowledge_documents()

    if not documents:
        return []

    if k is None:
        k = settings.rag_top_k

    k = max(1, min(k, len(documents)))

    vector_store = build_vector_store(documents)

    results = vector_store.similarity_search(
        query,
        k=k,
    )

    return [
        {
            "content": document.page_content,
            "source": document.metadata.get(
                "source",
                "",
            ),
            "filename": document.metadata.get(
                "filename",
                "",
            ),
            "category": document.metadata.get(
                "category",
                "",
            ),
        }
        for document in results
    ]


def retrieve_incident_knowledge(
    incident_id: str,
    description: str,
    service: str,
) -> list[dict[str, Any]]:
    """
    Retrieve knowledge specifically for an incident.
    """

    query = (
        f"Incident ID: {incident_id}. "
        f"Service: {service}. "
        f"Incident description: {description}. "
        "Find relevant runbooks, previous incidents, "
        "troubleshooting procedures, root-cause validation, "
        "database connection issues, HTTP 500 errors, "
        "deployment-related problems, and recommended "
        "investigation steps."
    )

    return retrieve_knowledge(
        query=query,
        k=settings.rag_top_k,
    )


def format_rag_context(
    results: list[dict[str, Any]],
) -> str:
    """
    Convert retrieved documents into a compact context string
    that can be passed to an LLM agent.
    """

    if not results:
        return "No relevant knowledge documents were retrieved."

    sections: list[str] = []

    for index, result in enumerate(results, 1):
        filename = result.get("filename", "Unknown")
        category = result.get("category", "Unknown")
        source = result.get("source", "Unknown")
        content = result.get("content", "")

        sections.append(
            f"DOCUMENT {index}\n"
            f"Filename: {filename}\n"
            f"Category: {category}\n"
            f"Source: {source}\n"
            f"Content:\n{content}"
        )

    return "\n\n---\n\n".join(sections)


if __name__ == "__main__":
    results = retrieve_incident_knowledge(
        incident_id="INC-001",
        description="API returning HTTP 500 errors",
        service="api",
    )

    print(
        f"Knowledge documents available: "
        f"{len(load_knowledge_documents())}"
    )

    print(
        f"Retrieved documents: "
        f"{len(results)}"
    )

    print()

    for index, result in enumerate(results, 1):
        print(
            f"{index}. "
            f"{result.get('filename', 'Unknown')}"
        )
        print(
            f"   Category: "
            f"{result.get('category', 'Unknown')}"
        )
        print(
            f"   Source: "
            f"{result.get('source', 'Unknown')}"
        )
        print()