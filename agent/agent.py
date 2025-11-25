from .prompts.peer_reviewer_prompt import PEER_REVIEWER_PROMPT
from .tools import fetch_url_context

from google.adk.agents.llm_agent import LlmAgent

capital_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="peer_review_agent",
    description="An Expert Peer Reviewer, a highly experienced editor and fact-checker for professional technical and non-technical blog posts.",
    instruction=PEER_REVIEWER_PROMPT,
    tools=[fetch_url_context],
    include_contents="none",
)
