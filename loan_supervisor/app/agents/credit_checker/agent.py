from google.adk.agents import Agent

from app.shared.model import model_instance
from app.shared.callbacks import before_agent_callback, create_after_model_callback


def get_credit_score(ssn: str) -> str:
    """
    Simulates a call to a credit bureau API to fetch the credit score for a given Social Security Number.

    Args:
        ssn: The Social Security Number as a string (e.g., "000-00-0000").

    Returns:
        The credit score as a string, or an error message if not found.
    """
    if ssn == "000-00-0000":
        return "The Credit Score is 680"
    elif ssn == "999-99-9999":
        return "The Credit Score is 500"
    else:
        return "Credit score not found for the provided SSN."


from app.app_utils import helpers
from google.adk.agents.readonly_context import ReadonlyContext


def _dynamic_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamically provides instructions to the agent by loading and formatting a prompt."""
    prompt = helpers.load_prompt_file_from_calling_agent()
    return prompt


credit_checker_agent = Agent(
    model=model_instance,
    name="Credit_Checker",
    description="Agent that validates credit scores by simulating calls to a credit bureau API using an SSN.",
    instruction=_dynamic_instruction_provider,
    # tools=[get_credit_score],
    before_agent_callback=before_agent_callback,
    after_model_callback=create_after_model_callback(agent_name="credit_checker"),
)
