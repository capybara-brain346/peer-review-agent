from google.adk.agents.llm_agent import LlmAgent

capital_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="peer_review_agent",
    description="An Expert Peer Reviewer, a highly experienced editor and fact-checker for professional technical and non-technical blog posts.",
)
