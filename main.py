import os
from livekit.agents import cli, WorkerOptions
from agent.intake_agent import entrypoint

def sanitize_url():
    url = os.getenv("LIVEKIT_URL", "")
    if url:
        # Remove protocols and trailing slashes
        clean = url.strip().lower()
        for prefix in ['wss://', 'ws://', 'https://', 'http://']:
            if clean.startswith(prefix):
                clean = clean[len(prefix):]
        clean = clean.rstrip('/')
        # Agents SDK prefers wss:// for the CLI connection usually, 
        # but let's standardize on the domain or wss:// if needed.
        # Most reliable is to set it back to wss:// for the worker.
        os.environ["LIVEKIT_URL"] = f"wss://{clean}"
        print(f"Normalized LIVEKIT_URL to: {os.environ['LIVEKIT_URL']}")

if __name__ == "__main__":
    sanitize_url()
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint,
                              agent_name = "intake_agent"))
