from google.adk.agents import Agent
from google.adk.tools import google_search


google_search_agent = Agent(
    model="gemini-2.5-flash",
    name="google_search_agent",
    description="Performs a google using google_search tool",
    instruction="""
    You are a search agent responsible for searching google for information requested by the user. Use the google_search
    """,
    tools=[google_search],
)
