from google.adk import Agent

from .prompt import return_descriptions_rag, return_instructions_rag

MODEL = "gemini-2.0-flash"

rag_agent = Agent(
    name="rag_agent",
    model=MODEL,
    description=return_descriptions_rag(),
    instruction=return_instructions_rag,
)
