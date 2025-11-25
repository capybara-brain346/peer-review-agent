from google.adk.agents.llm_agent import LlmAgent

capital_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="peer_review_agent",
    description="Answers user questions about the capital city of a given country.",
)
