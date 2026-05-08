import os
import tomllib
from google.adk.agents import Agent
from app.shared.model import model_instance
from app.shared.callbacks import before_agent_callback, create_after_model_callback
from app.app_utils import helpers
from google.adk.agents.readonly_context import ReadonlyContext


def summarize_response(app_id: str) -> str:
    """
    Deterministic search: Reads the responses.toml file, searches for the given
    application ID, and returns the verbatim response table.

    Args:
        app_id: The normalized application ID (e.g., 'L_0001').

    Returns:
        The verbatim response string from responses.toml.
    """
    try:
        # Locate responses.toml inside app/ directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(os.path.dirname(current_dir))
        toml_path = os.path.join(app_dir, "responses.toml")

        with open(toml_path, "rb") as f:
            data = tomllib.load(f)

        responses = data.get("responses", {})
        result = responses.get(app_id.upper()) or responses.get("L_0010")
        return result
    except Exception as e:
        return f"Error loading responses database: {str(e)}"


def _dynamic_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamically provides instructions to the agent by loading and formatting a prompt."""
    prompt = helpers.load_prompt_file_from_calling_agent()
    return prompt


summarization_agent = Agent(
    model=model_instance,
    name="Summarization_Agent",
    description="Agent that deterministic retrieves and returns the final verbatim underwriting summary response for a given application ID.",
    instruction=_dynamic_instruction_provider,
    tools=[summarize_response],
    before_agent_callback=before_agent_callback,
    after_model_callback=create_after_model_callback(agent_name="summarization_agent"),
)
