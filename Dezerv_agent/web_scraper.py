import asyncio
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

load_dotenv(override=True)

@function_tool
def scrape_website(url: str) -> str:
    """
    Extract text content from a website URL.

    Args:
        url (str): The website URL to scrape

    Returns:
        str: Extracted text content from the website
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        # Limit output length to avoid token overflow
        return text[:5000]

    except Exception as e:
        return f"Error scraping {url}: {str(e)}"


def create_agent() -> Agent:
    """
    Create and return the Research Agent
    """
    return Agent(
        name="ResearchAgent",
        instructions=(
            "You are a research agent that extracts and summarizes "
            "information from websites accurately."
        ),
        tools=[scrape_website],
        model="gpt-4o-mini"
    )


async def main():
    agent = create_agent()

     # 🔹 Take URL from user input
    url = input("Enter the website URL to scrape: ").strip()

    if not url:
        print("❌ No URL provided. Exiting.")
        return
    query = (
        f"Scrape information from the following website and provide a clear summary:\n{url}"
    )

    result = await Runner.run(agent, query)

    print("\n====== FINAL OUTPUT ======\n")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
