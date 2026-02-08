"""
Voice Assistant Tools
Functions that the voice assistant can call to perform actions
"""

import webbrowser
import logging
from typing import Annotated

logger = logging.getLogger(__name__)


def open_youtube_search(query: Annotated[str, "The search query for YouTube"]) -> str:
    """
    Opens YouTube in the default browser and searches for the given query.
    
    Args:
        query: The search term to look up on YouTube
        
    Returns:
        A confirmation message
    """
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        logger.info(f"Opening YouTube search for: {query}")
        return f"Opening YouTube and searching for '{query}'"
    except Exception as e:
        logger.error(f"Error opening YouTube: {e}")
        return f"Sorry, I couldn't open YouTube. Error: {str(e)}"


def open_website(url: Annotated[str, "The website URL to open"]) -> str:
    """
    Opens a website in the default browser.
    
    Args:
        url: The URL to open (e.g., 'https://google.com')
        
    Returns:
        A confirmation message
    """
    try:
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        webbrowser.open(url)
        logger.info(f"Opening website: {url}")
        return f"Opening {url}"
    except Exception as e:
        logger.error(f"Error opening website: {e}")
        return f"Sorry, I couldn't open that website. Error: {str(e)}"


def search_google(query: Annotated[str, "The search query for Google"]) -> str:
    """
    Opens Google in the default browser and searches for the given query.
    
    Args:
        query: The search term to look up on Google
        
    Returns:
        A confirmation message
    """
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        logger.info(f"Opening Google search for: {query}")
        return f"Searching Google for '{query}'"
    except Exception as e:
        logger.error(f"Error opening Google: {e}")
        return f"Sorry, I couldn't search Google. Error: {str(e)}"
