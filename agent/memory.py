import json
from typing import List, Dict, Any
from mem0 import Memory
from .utils.logger import logger


class MemoryManager:
    def __init__(self):
        config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "peer_review_memory",
                    "path": "agent/memory_store/chroma",
                },
            },
            "embedder": {
                "provider": "sentence-transformers",
                "config": {"model": "all-MiniLM-L6-v2"},
            },
            "history_store_path": "agent/memory_store/history.db",
        }

        try:
            logger.info(
                "Initializing MemoryManager with ChromaDB and SentenceTransformers"
            )
            self.memory = Memory.from_config(config)
        except Exception as e:
            logger.critical(f"Failed to initialize MemoryManager: {e}")
            raise

    def get_blog_history(self, blog_id: str) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Fetching history for blog_id: {blog_id}")
            history = self.memory.get_all(user_id=blog_id)
            return history
        except Exception as e:
            logger.error(f"Error retrieving history for blog_id {blog_id}: {e}")
            return []

    def store_review(self, blog_id: str, content: str, feedback: Any) -> None:
        try:
            logger.debug(f"Storing review for blog_id: {blog_id}")
            if hasattr(feedback, "model_dump_json"):
                feedback_str = feedback.model_dump_json()
            elif isinstance(feedback, dict):
                feedback_str = json.dumps(feedback)
            else:
                feedback_str = str(feedback)

            self.memory.add(
                feedback_str,
                user_id=blog_id,
                metadata={
                    "source": "peer_review_agent",
                    "type": "feedback",
                    "content_snippet": content[:200] if content else "",
                },
            )
            logger.info(f"Successfully stored review for {blog_id}")
        except Exception as e:
            logger.error(f"Error storing review for blog_id {blog_id}: {e}")
