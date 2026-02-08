from livekit.agents import cli, WorkerOptions
from agent.intake_agent import entrypoint

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint,
                              agent_name = "intake_agent"))
