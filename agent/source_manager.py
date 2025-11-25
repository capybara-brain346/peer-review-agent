import uuid
from typing import List, Set
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .utils.logger import logger


class SourceManager:
    def __init__(self, persistence_path: str = "agent/source_store"):
        try:
            logger.info(
                f"Initializing SourceManager with persistence path: {persistence_path}"
            )
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
        except Exception as e:
            logger.critical(f"Failed to initialize SourceManager: {e}")
            raise

    def add_source(self, content: str, source_name: str) -> None:
        if not content.strip():
            logger.warning(f"Attempted to add empty source: {source_name}")
            return

        try:
            logger.info(f"Adding source: {source_name}")
            raw_doc = Document(page_content=content, metadata={"source": source_name})

            docs = self.text_splitter.split_documents([raw_doc])

            if not docs:
                logger.warning(f"No chunks created for source: {source_name}")
                return

            for i, doc in enumerate(docs):
                doc.metadata["chunk_index"] = i
                doc.metadata["source"] = source_name
                doc.id = f"{source_name}_{i}_{str(uuid.uuid4())[:8]}"

            self.vector_store.add_documents(docs)
            logger.info(
                f"Successfully added source '{source_name}' with {len(docs)} chunks."
            )
        except Exception as e:
            logger.error(f"Error adding source {source_name}: {e}")

    def search_sources(self, query: str, k: int = 3) -> List[str]:
        try:
            logger.debug(f"Searching sources with query: '{query}' (k={k})")
            results = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"Found {len(results)} results")
            return [doc.page_content for doc in results]
        except Exception as e:
            logger.error(f"Error searching sources: {e}")
            return []

    def list_sources(self) -> List[str]:
        try:
            logger.debug("Listing available sources")
            result = self.vector_store._collection.get(include=["metadatas"])
            sources: Set[str] = set()
            if result["metadatas"]:
                for meta in result["metadatas"]:
                    if "source" in meta:
                        sources.add(meta["source"])
            logger.info(f"Found {len(sources)} unique sources")
            return list(sources)
        except Exception as e:
            logger.error(f"Error listing sources: {e}")
            return []

    def get_source_content(self, source_name: str) -> str:
        try:
            logger.debug(f"Retrieving content for source: {source_name}")
            result = self.vector_store._collection.get(
                where={"source": source_name}, include=["documents", "metadatas"]
            )

            if not result["documents"]:
                logger.warning(f"No documents found for source: {source_name}")
                return ""

            chunks_with_meta = zip(result["documents"], result["metadatas"])
            sorted_chunks = sorted(
                chunks_with_meta, key=lambda x: x[1].get("chunk_index", 0)
            )

            return "\n\n".join([chunk for chunk, _ in sorted_chunks])
        except Exception as e:
            logger.error(f"Error getting source content for {source_name}: {e}")
            return ""
