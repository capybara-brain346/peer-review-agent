import json
from typing import List, Dict, Any
from mem0 import Memory


class MemoryManager:
    def __init__(self):
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "path": "agent/memory_store/qdrant",
                },
            },
            "embedder": {
                "provider": "sentence-transformers",
                "config": {"model": "all-MiniLM-L6-v2"},
            },
            "history_store_path": "agent/memory_store/history.db",
        }

        self.memory = Memory.from_config(config)

    def get_blog_history(self, blog_id: str) -> List[Dict[str, Any]]:
        try:
            return self.memory.get_all(user_id=blog_id)
        except Exception as e:
            print(f"Error retrieving history for blog_id {blog_id}: {e}")
            return []

    def store_review(self, blog_id: str, content: str, feedback: Any) -> None:
        try:
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
        except Exception as e:
            print(f"Error storing review for blog_id {blog_id}: {e}")
