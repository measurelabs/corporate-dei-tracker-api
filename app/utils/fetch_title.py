"""Utility to fetch page titles from URLs."""
import httpx
from bs4 import BeautifulSoup
from typing import Optional
import asyncio


async def fetch_page_title(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetch the title from a web page URL.

    Args:
        url: The URL to fetch the title from
        timeout: Request timeout in seconds

    Returns:
        The page title, or None if unable to fetch
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to get Open Graph title first (more accurate for social media)
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()

            # Try Twitter title
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and twitter_title.get('content'):
                return twitter_title['content'].strip()

            # Fall back to regular title tag
            title_tag = soup.find('title')
            if title_tag and title_tag.string:
                return title_tag.string.strip()

            return None

    except Exception as e:
        print(f"Error fetching title for {url}: {str(e)}")
        return None


async def fetch_titles_batch(urls: list[str]) -> dict[str, Optional[str]]:
    """
    Fetch titles for multiple URLs concurrently.

    Args:
        urls: List of URLs to fetch titles for

    Returns:
        Dictionary mapping URLs to their titles
    """
    tasks = [fetch_page_title(url) for url in urls]
    titles = await asyncio.gather(*tasks, return_exceptions=True)

    result = {}
    for url, title in zip(urls, titles):
        if isinstance(title, Exception):
            result[url] = None
        else:
            result[url] = title

    return result
