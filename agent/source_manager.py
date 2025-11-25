import uuid
from typing import List, Set
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class SourceManager:
    def __init__(self, persistence_path: str = "agent/source_store"):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            collection_name="source_materials",
            embedding_function=self.embeddings,
            persist_directory=persistence_path,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def add_source(self, content: str, source_name: str) -> None:
        if not content.strip():
            return

        raw_doc = Document(page_content=content, metadata={"source": source_name})

        docs = self.text_splitter.split_documents([raw_doc])

        if not docs:
            return

        for i, doc in enumerate(docs):
            doc.metadata["chunk_index"] = i
            doc.metadata["source"] = source_name
            doc.id = f"{source_name}_{i}_{str(uuid.uuid4())[:8]}"

        self.vector_store.add_documents(docs)
        print(f"Added source '{source_name}' with {len(docs)} chunks.")

    def search_sources(self, query: str, k: int = 3) -> List[str]:
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def list_sources(self) -> List[str]:
        try:
            result = self.vector_store._collection.get(include=["metadatas"])
            sources: Set[str] = set()
            if result["metadatas"]:
                for meta in result["metadatas"]:
                    if "source" in meta:
                        sources.add(meta["source"])
            return list(sources)
        except Exception as e:
            print(f"Error listing sources: {e}")
            return []

    def get_source_content(self, source_name: str) -> str:
        try:
            result = self.vector_store._collection.get(
                where={"source": source_name}, include=["documents", "metadatas"]
            )

            if not result["documents"]:
                return ""

            chunks_with_meta = zip(result["documents"], result["metadatas"])
            sorted_chunks = sorted(
                chunks_with_meta, key=lambda x: x[1].get("chunk_index", 0)
            )

            return "\n\n".join([chunk for chunk, _ in sorted_chunks])
        except Exception as e:
            print(f"Error getting source content: {e}")
            return ""
