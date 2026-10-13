import os
import sys
from google.adk.agents import LlmAgent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_loader import load_instructions_file
from tools.file_writer_tool import write_text_file
from utils.bedrock_llm import BedrockLlm  # noqa: F401 — registers bedrock/... model

# ✅ COMPLETE WORKED EXAMPLE – copy this pattern for the other five agents.
market_researcher_agent = LlmAgent(
    name="market_researcher_agent",
    model="bedrock/amazon.nova-lite-v1:0",
    instruction=load_instructions_file("agents/market_researcher/instructions.txt"),
    description=load_instructions_file("agents/market_researcher/description.txt"),
    tools=[write_text_file],
    output_key="market_research_output"
)
