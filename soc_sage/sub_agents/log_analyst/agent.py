from google.adk import Agent

from .prompt import return_descriptions_analyst, return_instructions_analyst

MODEL = "gemini-2.0-flash"

log_analyst_agent = Agent(
    name="log_analyst",
    model=MODEL,
    description=return_descriptions_analyst(),
    instruction=return_instructions_analyst(),
)
