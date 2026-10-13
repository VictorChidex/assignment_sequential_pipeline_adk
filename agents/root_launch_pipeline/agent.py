import os
import sys
from google.adk.agents import SequentialAgent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_loader import load_instructions_file
from agents.market_researcher.agent import market_researcher_agent
# TODO: import the other five agents as you finish them, e.g.
# from agents.persona_builder.agent import persona_builder_agent
# from agents.product_strategist.agent import product_strategist_agent
# from agents.copywriter.agent import copywriter_agent
# from agents.landing_page_builder.agent import landing_page_builder_agent
# from agents.qa_reviewer.agent import qa_reviewer_agent

root_agent = SequentialAgent(
    name="root_launch_pipeline_agent",
    # TODO: add the agents in order. Add ONE at a time and run after each.
    sub_agents=[
        market_researcher_agent,
    ],
    description=load_instructions_file("agents/root_launch_pipeline/description.txt")
)
