from google.adk.agents import Agent

from .prompts import return_descriptions_root, return_instructions_root

MODEL = "gemini-2.0-flash"

root_agent = Agent(
    name="alert_receiver",
    model=MODEL,
    description=return_descriptions_root(),
    instruction=return_instructions_root(),
)
