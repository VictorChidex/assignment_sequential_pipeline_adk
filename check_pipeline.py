# =============================================================================
# FILE: check_pipeline.py
# PURPOSE:
#   Checks your pipeline against the assignment contract WITHOUT calling the
#   LLM. Run it any time:   uv run check_pipeline.py
#   The instructor runs the same script when grading.
# =============================================================================

import re
from pathlib import Path

from google.adk.agents import LlmAgent, SequentialAgent

from agents.root_launch_pipeline.agent import root_agent

# (agent name, output_key, state keys its instructions must reference)
CONTRACT = [
    ("market_researcher_agent", "market_research_output", []),
    ("persona_builder_agent", "personas_output", ["market_research_output"]),
    ("product_strategist_agent", "product_strategy_output", ["market_research_output", "personas_output"]),
    ("copywriter_agent", "marketing_copy_output", ["personas_output", "product_strategy_output"]),
    ("landing_page_builder_agent", "landing_page_output", ["product_strategy_output", "marketing_copy_output"]),
    ("qa_reviewer_agent", "qa_review_output", ["product_strategy_output", "marketing_copy_output", "landing_page_output"]),
]

FILE_WRITER_TOOLS = {"write_text_file", "write_html_file"}

passed, failed = 0, 0


def check(ok: bool, message: str) -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"  [PASS] {message}")
    else:
        failed += 1
        print(f"  [FAIL] {message}")


print("\nRoot agent")
check(isinstance(root_agent, SequentialAgent), "root_agent is a SequentialAgent")
sub_agents = list(root_agent.sub_agents)
check(len(sub_agents) == 6, f"has 6 sub agents (found {len(sub_agents)})")

custom_tools = set()

for index, (name, output_key, reads) in enumerate(CONTRACT):
    print(f"\nAgent {index + 1}: {name}")
    agent = sub_agents[index] if index < len(sub_agents) else None
    if agent is None:
        check(False, "agent is in sub_agents")
        continue

    check(agent.name == name, f"position {index + 1} is '{name}' (found '{agent.name}')")
    check(isinstance(agent, LlmAgent), "is an LlmAgent")
    check(agent.output_key == output_key, f"output_key == '{output_key}' (found '{agent.output_key}')")

    instruction = agent.instruction if isinstance(agent.instruction, str) else ""
    check(len(instruction) > 300, "instructions.txt is written (> 300 chars)")
    check("TODO" not in instruction, "instructions.txt has no TODO left")
    check("state['" not in instruction, "uses {key} placeholders, not state['key']")
    for key in reads:
        check(re.search(r"\{" + key + r"\??\}", instruction) is not None, f"reads {{{key}}}")

    tool_names = {getattr(t, "__name__", getattr(t, "name", str(t))) for t in agent.tools}
    check(len(tool_names) > 0, f"has at least one tool ({', '.join(sorted(tool_names)) or 'none'})")
    custom_tools |= tool_names - FILE_WRITER_TOOLS

print("\nTools")
check(len(custom_tools) >= 1, f"at least one custom (non file-writer) tool ({', '.join(sorted(custom_tools)) or 'none'})")

print("\nOutput folder")
outputs = [p for p in Path("output").glob("*") if p.name != ".gitkeep"]
check(len(outputs) >= 4, f"at least 4 files in output/ (found {len(outputs)})")

print(f"\nResult: {passed} passed, {failed} failed\n")
