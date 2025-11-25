import asyncio
from dotenv import load_dotenv
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from google.adk.tools import FunctionTool, agent_tool
from google.adk.agents.llm_agent import LlmAgent

from agent.prompts.peer_reviewer_prompt import PEER_REVIEWER_PROMPT
from agent.tools import fetch_url_context, retrieve_source_context
from agent.schemas import PeerReviewReport
from agent.memory import MemoryManager
from agent.sub_agents.google_search_agent import google_search_agent
from agent.utils.logger import logger


load_dotenv()


peer_review_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="peer_review_agent",
    description="An Expert Peer Reviewer, a highly experienced editor and fact-checker for professional technical and non-technical blog posts.",
    instruction=PEER_REVIEWER_PROMPT,
    tools=[
        FunctionTool(fetch_url_context),
        FunctionTool(retrieve_source_context),
        agent_tool.AgentTool(google_search_agent),
    ],
    include_contents="none",
    output_schema=PeerReviewReport,
)


async def run_peer_review_async(blog_id: str, content: str) -> PeerReviewReport:
    logger.info(f"Starting async peer review for blog_id: {blog_id}")

    memory_manager = await asyncio.to_thread(MemoryManager)

    past_feedback = await asyncio.to_thread(memory_manager.get_blog_history, blog_id)
    past_feedback_text = (
        json.dumps(past_feedback)
        if past_feedback
        else "No previous feedback available."
    )
    logger.debug(f"Retrieved {len(past_feedback)} past feedback items")

    session_id = f"session_{blog_id}"
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="peer_review_app", user_id=blog_id, session_id=session_id
    )

    runner = Runner(
        agent=peer_review_agent,
        app_name="peer_review_app",
        session_service=session_service,
    )

    review_prompt = f"""Please review the following blog content:

**Blog Content:**
{content}

**Past Feedback Context:**
{past_feedback_text}

**Source Context:**
Use the retrieve_source_context tool if you need to verify information against internal knowledge base.

Provide a comprehensive peer review report following the output schema requirements."""

    logger.info("Executing runner.run_async")

    full_response = ""
    report = None

    async for event in runner.run_async(
        user_id=blog_id,
        session_id=session_id,
        new_message=genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text=review_prompt)]
        ),
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                full_response = event.content.parts[0].text
                logger.debug(
                    f"Received final response: {len(full_response)} characters"
                )

            if hasattr(event, "structured_response") and event.structured_response:
                report = event.structured_response
                logger.info(
                    "Successfully received structured PeerReviewReport from agent"
                )
            break

    if not report and not full_response:
        logger.error("No response received from agent")
        raise ValueError("Agent did not produce a response")

    if not report:
        try:
            response_text = full_response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            report_data = json.loads(response_text)
            report = PeerReviewReport(**report_data)
            logger.info("Successfully parsed PeerReviewReport from JSON")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {full_response}")
            raise ValueError(f"Agent response was not valid JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing review report: {e}")
            raise

    await asyncio.to_thread(memory_manager.store_review, blog_id, content, report)
    logger.info(f"Stored review in memory for blog_id: {blog_id}")

    return report


class PeerReviewer:
    """
    Synchronous wrapper for the async peer review agent.
    Provides convenience method for non-async environments.
    """

    @staticmethod
    def review_blog(blog_id: str, content: str) -> PeerReviewReport:
        """
        Synchronous convenience method that internally uses asyncio.run.
        For async applications, prefer using run_peer_review_async directly.
        """
        logger.info(f"Using synchronous wrapper for blog_id: {blog_id}")
        return asyncio.run(run_peer_review_async(blog_id, content))


peer_reviewer = PeerReviewer()
