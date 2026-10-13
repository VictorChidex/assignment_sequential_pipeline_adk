import os
import sys
from google.adk.agents import LlmAgent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_loader import load_instructions_file
# TODO: import the tool(s) this agent needs from tools.file_writer_tool
# Suggested: write_text_file (+ optional check_html)
from utils.bedrock_llm import BedrockLlm  # noqa: F401 — registers bedrock/... model

# ✏️  AGENT 6 – TODO
# Look at agents/market_researcher/agent.py for the complete pattern.
qa_reviewer_agent = LlmAgent(
    name="qa_reviewer_agent",                     # do not change (used for grading)
    model="bedrock/amazon.nova-lite-v1:0",
    instruction=load_instructions_file("agents/qa_reviewer/instructions.txt"),
    description=load_instructions_file("agents/qa_reviewer/description.txt"),
    tools=[],                                  # TODO: add tool(s), e.g. [write_text_file]
    # TODO: add output_key="qa_review_output"
)
