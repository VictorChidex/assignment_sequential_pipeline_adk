# --- A. IMPORTING THE NECESSARY TOOLS ---
import asyncio
import json
from typing import Any
from rich import print as rprint
from rich.syntax import Syntax

from google.genai.types import Content, Part

from dotenv import load_dotenv
load_dotenv()

# --- B. IMPORTING OUR AGENT ---
from agents.root_launch_pipeline.agent import root_agent

# --- C. IMPORTING ADK (AGENT DEVELOPMENT KIT) COMPONENTS ---
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# --- 1. SETTING UP IDENTIFIERS (CONSTANTS) ---
APP_NAME = "launchpad_app"
USER_ID = "user_12345"
SESSION_ID = "session_launchpad_1"

# TODO: change this to the name of the LAST agent in your pipeline
# (start with "market_researcher_agent", end with "qa_reviewer_agent").
FINAL_AGENT_NAME = "qa_reviewer_agent"

# Set to False to hide the full JSON of every event and only see the summary.
SHOW_EVENTS = False


# --- 2. THE MAIN CHAT LOOP FUNCTION ---
async def chat_loop():
    """
    Initializes the agent and session, then loops to accept product ideas
    and run them through the sequential pipeline.
    """
    print("LaunchPad Pipeline Started.")
    print("Type 'quit', 'exit', or ':q' to end the session.\n")

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    while True:
        user_query = input("Enter your product idea: ")

        if user_query.lower() in ["quit", "exit", ":q"]:
            print("Ending chat session. Goodbye!")
            break

        new_message = Content(role="user", parts=[Part(text=user_query)])

        events = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=new_message
        )

        # --- Process the Event Stream ---
        i = 0
        async for event in events:
            i += 1
            if SHOW_EVENTS:
                print_json_response(event, f"============Event #{i} ({event.author})=============")

            # Print a short line each time an agent finishes, so you can see the sequence.
            if event.is_final_response() and event.content and event.content.parts:
                rprint(f"[green bold]✔ {event.author} finished[/green bold]")

                if event.author == FINAL_AGENT_NAME:
                    final_response = event.content.parts[0].text or ""
                    print(f"\nFinal Agent Response:\n------------------------\n{final_response}\n")
                    break

        # --- Show what every agent saved to state (output_key) ---
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print_state_summary(session.state)


# -----------------------------------------------------------------------------
# Helper: show which output_keys are in state and how long each value is
# -----------------------------------------------------------------------------
def print_state_summary(state: dict) -> None:
    rprint("\n[cyan bold]=== Session State (output_keys) ===[/cyan bold]")
    if not state:
        rprint("[red]State is empty – did your agents set output_key?[/red]")
        return
    for key, value in state.items():
        preview = str(value).replace("\n", " ")[:80]
        rprint(f"[yellow]{key}[/yellow] ({len(str(value))} chars): {preview}...")


# -----------------------------------------------------------------------------
# Helper: Pretty print JSON objects using syntax coloring
# -----------------------------------------------------------------------------
def print_json_response(response: Any, title: str) -> None:
    print(f"\n=== {title} ===")
    try:
        if hasattr(response, "root"):
            data = response.root.model_dump(mode="json", exclude_none=True)
        else:
            data = response.model_dump(mode="json", exclude_none=True)

        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        rprint(syntax)
    except Exception as e:
        rprint(f"[red bold]Error printing JSON:[/red bold] {e}")
        rprint(repr(response))


# --- 3. STARTING THE PROGRAM ---
if __name__ == '__main__':
    asyncio.run(chat_loop())
