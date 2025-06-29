from google.adk import Agent

from .prompt import return_descriptions_writer, return_instructions_writer

MODEL = "gemini-2.0-flash"

report_writer_agent = Agent(
    name="report_writer",
    model=MODEL,
    description=return_descriptions_writer(),
    instruction=return_instructions_writer(),
)
