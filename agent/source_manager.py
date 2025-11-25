import uuid
from typing import List, Set
import chromadb
from chromadb.utils import embedding_functions


class SourceManager:
    def __init__(self, persistence_path: str = "agent/source_store"):
        self.client = chromadb.PersistentClient(path=persistence_path)

        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )

        self.collection = self.client.get_or_create_collection(
            name="source_materials", embedding_function=self.embedding_function
        )

    def add_source(self, content: str, source_name: str) -> None:
        chunks = [p.strip() for p in content.split("\n\n") if p.strip()]

        if not chunks:
            return

        ids = [f"{source_name}_{i}_{str(uuid.uuid4())[:8]}" for i in range(len(chunks))]

        metadatas = [
            {"source": source_name, "chunk_index": i} for i in range(len(chunks))
        ]

        self.collection.add(documents=chunks, metadatas=metadatas, ids=ids)
        print(f"Added source '{source_name}' with {len(chunks)} chunks.")

    def search_sources(self, query: str, k: int = 3) -> List[str]:
        results = self.collection.query(query_texts=[query], n_results=k)

        if results and results["documents"]:
            return results["documents"][0]
        return []

    def list_sources(self) -> List[str]:
        result = self.collection.get(include=["metadatas"])

        sources: Set[str] = set()
        if result["metadatas"]:
            for meta in result["metadatas"]:
                if "source" in meta:
                    sources.add(meta["source"])

        return list(sources)

    def get_source_content(self, source_name: str) -> str:
        result = self.collection.get(
            where={"source": source_name}, include=["documents", "metadatas"]
        )

        if not result["documents"]:
            return ""

        chunks_with_meta = zip(result["documents"], result["metadatas"])
        sorted_chunks = sorted(
            chunks_with_meta, key=lambda x: x[1].get("chunk_index", 0)
        )

        return "\n\n".join([chunk for chunk, _ in sorted_chunks])
