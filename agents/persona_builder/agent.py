import os
import sys
from google.adk.agents import LlmAgent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_loader import load_instructions_file
# TODO: import the tool(s) this agent needs from tools.file_writer_tool
# Suggested: write_text_file
from utils.bedrock_llm import BedrockLlm  # noqa: F401 — registers bedrock/... model

# ✏️  AGENT 2 – TODO
# Look at agents/market_researcher/agent.py for the complete pattern.
persona_builder_agent = LlmAgent(
    name="persona_builder_agent",                     # do not change (used for grading)
    model="bedrock/amazon.nova-lite-v1:0",
    instruction=load_instructions_file("agents/persona_builder/instructions.txt"),
    description=load_instructions_file("agents/persona_builder/description.txt"),
    tools=[],                                  # TODO: add tool(s), e.g. [write_text_file]
    # TODO: add output_key="personas_output"
)
