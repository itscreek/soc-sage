from google.adk.agents import Agent
from google.adk.agents import LoopAgent, SequentialAgent

import prompts
from sub_agents.assessor import assessor_agent
from sub_agents.log_analyst import log_analyst_agent
from sub_agents.rag import rag_agent
from sub_agents.report_writer import report_writer_agent

MODEL = "gemini-2.0-flash"

analysis_loop = LoopAgent(
    name="analysis_loop",
    model=MODEL,
    description=prompts.return_descriptions_analysis_loop(),
    instruction=prompts.return_instructions_analysis_loop(),
    sub_agents=[
        log_analyst_agent,
        rag_agent,
    ],
    max_iterations=5,
)

incident_response_team = SequentialAgent(
    name="incident_response_team",
    model=MODEL,
    description=prompts.return_descriptions_response_team(),
    instruction=prompts.return_instructions_response_team(),
    sub_agents=[
        analysis_loop,
        assessor_agent,
        report_writer_agent,
    ],
)

root_agent = Agent(
    name="alert_receiver",
    model=MODEL,
    description=prompts.return_descriptions_root(),
    instruction=prompts.return_instructions_root(),
    sub_agents=[
        incident_response_team,
    ],
)
