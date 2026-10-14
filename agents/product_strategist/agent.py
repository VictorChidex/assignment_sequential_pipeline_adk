import os
import sys
from google.adk.agents import LlmAgent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_loader import load_instructions_file
# TODO: import the tool(s) this agent needs from tools.file_writer_tool
# Suggested: write_text_file + YOUR CUSTOM TOOL (e.g. calculate_pricing)
from tools.file_writer_tool import write_text_file
from tools.file_writer_tool import calculate_pricing
from utils.bedrock_llm import BedrockLlm  # noqa: F401 — registers bedrock/... model

# ✏️  AGENT 3 – TODO
# Look at agents/market_researcher/agent.py for the complete pattern.
product_strategist_agent = LlmAgent(
    name="product_strategist_agent",                     # do not change (used for grading)
    model="bedrock/amazon.nova-lite-v1:0",
    instruction=load_instructions_file("agents/product_strategist/instructions.txt"),
    description=load_instructions_file("agents/product_strategist/description.txt"),
    tools=[write_text_file, calculate_pricing],     # TODO: add tool(s), e.g. [write_text_file]
    # TODO: add output_key="product_strategy_output"
    output_key="product_strategy_output"
)
