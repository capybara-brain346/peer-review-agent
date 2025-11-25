from .prompts.peer_reviewer_prompt import PEER_REVIEWER_PROMPT
from .tools import fetch_url_context, retrieve_source_context, google_search
from .schemas import PeerReviewReport
from .memory import MemoryManager

from google.adk.agents.llm_agent import LlmAgent

memory_manager = MemoryManager()


class PeerReviewer(LlmAgent):
    def __init__(self, model: str = "gemini-2.5-flash"):
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
        history = memory_manager.get_blog_history(blog_id)

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

        user_input = f"""
        Review the following blog content:
        
        BLOG CONTENT:
        {content}
        
        PAST FEEDBACK CONTEXT:
        {history_context}
        """

        response = self.run(user_input)

        if isinstance(response, PeerReviewReport):
            memory_manager.store_review(blog_id, content, response)

        return response


peer_reviewer = PeerReviewer()
