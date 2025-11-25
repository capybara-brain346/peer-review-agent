import requests
from bs4 import BeautifulSoup
from .source_manager import SourceManager
from .utils.logger import logger


def fetch_url_context(url: str) -> str:
    logger.info(f"Fetching URL content: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()

        if "text/html" in content_type:
            logger.debug("Parsing HTML content")
            soup = BeautifulSoup(response.text, "html.parser")

            for script_or_style in soup(["script", "style", "nav", "footer"]):
                script_or_style.decompose()

            text = soup.get_text(separator="\n")

            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            result = "\n".join(chunk for chunk in chunks if chunk)
            logger.info(f"Successfully fetched {len(result)} characters from URL")
            return result

        logger.debug("Returning raw text content")
        return response.text

    except Exception as e:
        logger.error(f"Error fetching content from {url}: {str(e)}")
        return f"Error fetching content from {url}: {str(e)}"


try:
    source_manager = SourceManager()
except Exception as e:
    logger.critical(f"Failed to initialize SourceManager in tools: {e}")
    source_manager = None


def retrieve_source_context(query: str) -> str:
    logger.info(f"Retrieving source context for query: '{query}'")

    if not source_manager:
        logger.error("SourceManager not initialized")
        return "Error: Knowledge base unavailable."

    results = source_manager.search_sources(query, k=5)
    if not results:
        logger.info("No relevant source context found")
        return "No relevant source context found."

    logger.debug(f"Returning {len(results)} chunks of context")
    return "\n---\n".join(results)
