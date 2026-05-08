from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse

def before_agent_callback(callback_context: CallbackContext) -> None:
    """Callback before each agent call to initialize state."""
    callback_context.state["step"] = 0


def create_after_model_callback(agent_name: str):
    """Factory to create an after_model_callback that correctly captures the agent's name."""
    def after_model_callback(
        callback_context: CallbackContext, llm_response: LlmResponse
    ) -> None:
        state = callback_context.state
        llm_response.custom_metadata = {
            "function_call_id": "FunctionCallId_{}".format(state.get("step", 0)),
            "agent_name": agent_name,
        }
        state["step"] = state.get("step", 0) + 1

    return after_model_callback
