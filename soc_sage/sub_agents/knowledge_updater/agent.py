from google.adk import Agent

from .prompt import return_descriptions_updater, return_instructions_updater

MODEL = "gemini-2.0-flash"

knowledge_updater_agent = Agent(
    name="knowledge_updater",
    model=MODEL,
    description=return_descriptions_updater(),
    instruction=return_instructions_updater(),
)
