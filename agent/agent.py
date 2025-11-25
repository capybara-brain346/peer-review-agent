from dotenv import load_dotenv
from google.adk.tools import FunctionTool, agent_tool
from google.adk.agents.llm_agent import LlmAgent

from agent.prompts.peer_reviewer_prompt import PEER_REVIEWER_PROMPT
from agent.tools import fetch_url_context, retrieve_source_context
from agent.schemas import PeerReviewReport
from agent.sub_agents.google_search_agent import google_search_agent


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
