import requests
from bs4 import BeautifulSoup
from typing import List
from google.adk.tools import google_search
from .source_manager import SourceManager


def fetch_url_context(url: str) -> str:
    """
    Fetches the content of the url as plain text
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()

        if "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")

            for script_or_style in soup(["script", "style", "nav", "footer"]):
                script_or_style.decompose()

            text = soup.get_text(separator="\n")

            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return "\n".join(chunk for chunk in chunks if chunk)

        return response.text

    except Exception as e:
        return f"Error fetching content from {url}: {str(e)}"


source_manager = SourceManager()


def retrieve_source_context(query: str) -> str:
    results = source_manager.search_sources(query, k=5)
    if not results:
        return "No relevant source context found."

    return "\n---\n".join(results)
