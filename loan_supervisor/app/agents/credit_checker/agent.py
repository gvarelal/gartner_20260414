import os
import re
import tomllib
from google.adk.agents import Agent

from app.shared.model import model_instance
from app.shared.callbacks import before_agent_callback, create_after_model_callback
from app.app_utils import helpers
from google.adk.agents.readonly_context import ReadonlyContext


def retrieve_bureau_credit_profile(application_id: str) -> str:
    """
    Retrieves the bureau credit profile (FICO, delinquencies, balances) for a given loan application ID.

    Args:
        application_id: The loan application ID (e.g., 'L_0001').

    Returns:
        A formatted string detailing the credit profile retrieved from the bureau.
    """
    try:
        # Normalize ID to standard format L_XXXX
        match = re.search(r"L_?\d+", application_id, re.IGNORECASE)
        if not match:
            return "Invalid application ID format."
        
        num_part = "".join(filter(str.isdigit, match.group(0)))
        normalized_id = f"L_{int(num_part):04d}"
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        toml_path = os.path.join(current_dir, "..", "..", "responses.toml")

        with open(toml_path, "rb") as f:
            data = tomllib.load(f)

        checker_data = data.get("credit_checker", {})
        return checker_data.get(normalized_id, f"No preconfigured credit bureau profile found for {normalized_id}.")
    except Exception as e:
        return f"Error retrieving credit profile: {str(e)}"


def _dynamic_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamically provides instructions to the agent by loading and formatting a prompt."""
    prompt = helpers.load_prompt_file_from_calling_agent()
    return prompt


credit_checker_agent = Agent(
    model=model_instance,
    name="Credit_Checker",
    description="Agent that retrieves and validates bureau credit profiles for a given loan application ID.",
    instruction=_dynamic_instruction_provider,
    tools=[retrieve_bureau_credit_profile],
    before_agent_callback=before_agent_callback,
    after_model_callback=create_after_model_callback(agent_name="credit_checker"),
)
