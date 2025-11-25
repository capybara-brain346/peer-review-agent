Peer Review Agent

An AI-powered peer review system for blog posts and technical content. The agent provides detailed feedback on accuracy, clarity, tone, and structure using Google's Gemini model.

Features

- Reviews blog content from text input or URLs
- Fact-checks claims using Google search
- Maintains memory of past reviews to track recurring issues
- Generates structured reports with major/minor issues and line-by-line comments
- Export reviews as PDF
- Web interface built with Streamlit

Installation

Install dependencies using uv:

uv sync

Set up your environment variables in a .env file:

GOOGLE_API_KEY=your_api_key_here

Usage

Run the Streamlit app:

streamlit run app.py

The interface allows you to:

- Upload source materials for the knowledge base
- Submit blog content via text or URL
- Get comprehensive review reports
- Download PDF reports

Components

- agent/agent.py - Core review logic using Google ADK
- agent/tools.py - Tools for URL fetching and source retrieval
- agent/memory.py - Memory management for tracking review history
- agent/source_manager.py - Knowledge base for reference materials
- agent/sub_agents/google_search_agent.py - Sub-agent for external fact-checking
- app.py - Streamlit web interface

Requirements

- Python 3.10+
- Google Gemini API key
- Dependencies managed via pyproject.toml
