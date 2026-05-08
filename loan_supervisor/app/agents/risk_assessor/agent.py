import json
from google.adk.agents import Agent

from app.shared.model import model_instance
from app.shared.callbacks import before_agent_callback, create_after_model_callback


def calculate_risk_score(loan_amount: int, income: str, credit_score: int) -> str:
    """
    Calculates financial risk scores (1-10) based on loan amount, income, and credit score.

    Args:
        loan_amount: The requested loan amount.
        income: The applicant's monthly or annual income string.
        credit_score: The applicant's credit score.

    Returns:
        A JSON string containing the calculated 'risk_score'.
    """
    try:
        income_val = int("".join(filter(str.isdigit, income)))
        ratio = loan_amount / (income_val)
        risk = 5 if ratio > 0.5 else 2
        if credit_score < 700:
            risk += 3
        return json.dumps({"risk_score": min(risk, 10)})
    except Exception:
        # Default to highest risk if calculation fails
        return json.dumps({"risk_score": 10})


from app.app_utils import helpers
from google.adk.agents.readonly_context import ReadonlyContext


def _dynamic_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamically provides instructions to the agent by loading and formatting a prompt."""
    prompt = helpers.load_prompt_file_from_calling_agent()
    return prompt


risk_assessor_agent = Agent(
    model=model_instance,
    name="Risk_Assessor",
    description="Agent that calculates a financial risk score (1-10) based on loan amount, income, and credit score.",
    instruction=_dynamic_instruction_provider,
    # tools=[calculate_risk_score],
    before_agent_callback=before_agent_callback,
    after_model_callback=create_after_model_callback(agent_name="risk_assessor"),
)
