import os
from dotenv import load_dotenv
from google.adk.tools import FunctionTool, agent_tool
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from agent.prompts.peer_reviewer_prompt import PEER_REVIEWER_PROMPT
from agent.tools import fetch_url_context, retrieve_source_context
from agent.schemas import PeerReviewReport
from agent.sub_agents.google_search_agent import google_search_agent

load_dotenv()


def get_model():
    model_provider = os.getenv("MODEL_PROVIDER", "").lower()

    if model_provider == "gemini" or not model_provider:
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        return gemini_model

    elif model_provider == "ollama":
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        return LiteLlm(model=f"ollama_chat/{ollama_model}", api_base=ollama_base_url)

    elif model_provider == "openai":
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        return LiteLlm(model=openai_model, api_key=openai_api_key)

    elif model_provider == "claude":
        claude_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        return LiteLlm(model=claude_model, api_key=anthropic_api_key)

    else:
        raise ValueError(f"Unsupported MODEL_PROVIDER: {model_provider}")


model = get_model()

peer_review_agent = LlmAgent(
    model=model,
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
