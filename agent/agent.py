from .prompts.peer_reviewer_prompt import PEER_REVIEWER_PROMPT
from .tools import fetch_url_context, retrieve_source_context, google_search
from .schemas import PeerReviewReport
from .memory import MemoryManager
from .utils.logger import logger

from google.adk.agents.llm_agent import LlmAgent

memory_manager = MemoryManager()


class PeerReviewer(LlmAgent):
    def __init__(self, model: str = "gemini-2.5-flash"):
        logger.info(f"Initializing PeerReviewer with model: {model}")
        super().__init__(
            model=model,
            name="peer_review_agent",
            description="An Expert Peer Reviewer, a highly experienced editor and fact-checker for professional technical and non-technical blog posts.",
            instruction=PEER_REVIEWER_PROMPT,
            tools=[fetch_url_context, retrieve_source_context, google_search],
            include_contents="none",
            output_schema=PeerReviewReport,
        )

    def review_blog(self, blog_id: str, content: str) -> PeerReviewReport:
        logger.info(f"Starting review for blog_id: {blog_id}")

        try:
            history = memory_manager.get_blog_history(blog_id)
            logger.debug(f"Retrieved {len(history)} past feedback items for {blog_id}")
        except Exception as e:
            logger.error(f"Failed to retrieve history for {blog_id}: {e}")
            history = []

        history_context = (
            "\n".join(
                [
                    f"- Date: {h.get('created_at', 'Unknown')}\n  Feedback: {h.get('memory', '')}"
                    for h in history
                ]
            )
            if history
            else "No previous feedback found."
        )

        logger.debug("Constructing user input for agent")
        user_input = f"""
        Review the following blog content:
        
        BLOG CONTENT:
        {content}
        
        PAST FEEDBACK CONTEXT:
        {history_context}
        """

        logger.info("Sending request to LLM agent")
        try:
            response = self.run(user_input)
            logger.info("Received response from LLM agent")
        except Exception as e:
            logger.error(f"Error during agent execution: {e}")
            raise

        if isinstance(response, PeerReviewReport):
            try:
                memory_manager.store_review(blog_id, content, response)
                logger.info(f"Stored review for {blog_id} in memory")
            except Exception as e:
                logger.error(f"Failed to store review in memory: {e}")
        else:
            logger.warning(
                f"Unexpected response type: {type(response)}. Skipping memory storage."
            )

        return response


peer_reviewer = PeerReviewer()
