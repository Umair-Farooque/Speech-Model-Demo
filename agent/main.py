import logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, cli, function_tool, RunContext
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, silero
import webbrowser

# Load environment variables
load_dotenv()

logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)


# Define function tools that the agent can use
@function_tool()
async def open_youtube_search(context: RunContext, query: str):
    """
    Opens YouTube in the default browser and searches for the given query.
    
    Args:
        query: The search term to look up on YouTube (e.g., "blue eyes")
    """
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        logger.info(f"Opening YouTube search for: {query}")
        return f"Opening YouTube and searching for '{query}'"
    except Exception as e:
        logger.error(f"Error opening YouTube: {e}")
        return f"Sorry, I couldn't open YouTube"


@function_tool()
async def search_google(context: RunContext, query: str):
    """
    Opens Google in the default browser and searches for the given query.
    
    Args:
        query: The search term to look up on Google
    """
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        logger.info(f"Opening Google search for: {query}")
        return f"Searching Google for '{query}'"
    except Exception as e:
        logger.error(f"Error opening Google: {e}")
        return f"Sorry, I couldn't search Google"


@function_tool()
async def open_website(context: RunContext, url: str):
    """
    Opens a website in the default browser.
    
    Args:
        url: The website URL to open (e.g., 'google.com' or 'https://reddit.com')
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        webbrowser.open(url)
        logger.info(f"Opening website: {url}")
        return f"Opening {url}"
    except Exception as e:
        logger.error(f"Error opening website: {e}")
        return f"Sorry, I couldn't open that website"


async def entrypoint(ctx: JobContext):
    """Main entry point for the voice agent"""
    
    await ctx.connect()
    logger.info(f"Connected to room: {ctx.room.name}")
    
    # Create basic agent without tools for testing
    my_agent = Agent(
        instructions=(
            "You are a friendly and helpful AI voice assistant. "
            "Keep your responses concise and conversational since this is a voice interface. "
            "Be natural, warm, and engaging in your communication style."
        )
    )
    
    # Create session with VAD, STT, LLM, TTS
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
    )
    
    # Start the session with room and agent as named parameter
    await session.start(room=ctx.room, agent=my_agent)
    
    # Generate greeting
    await session.generate_reply(instructions="Greet the user and offer your assistance.")
    
    logger.info("Voice assistant started successfully")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
