import requests
from bs4 import BeautifulSoup


def fetch_url_context(url: str) -> str:
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
