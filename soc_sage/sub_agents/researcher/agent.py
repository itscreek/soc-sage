from google.adk import Agent

from .prompt import return_descriptions_researcher, return_instructions_researcher

MODEL = "gemini-2.0-flash"

researcher_agent = Agent(
    name="researcher",
    model=MODEL,
    description=return_descriptions_researcher(),
    instruction=return_instructions_researcher(),
)
