from google.adk import Agent

from .prompt import return_descriptions_assessor, return_instructions_assessor

MODEL = "gemini-2.0-flash"

assessor_agent = Agent(
    name="assessor",
    model=MODEL,
    description=return_descriptions_assessor(),
    instruction=return_instructions_assessor(),
)
