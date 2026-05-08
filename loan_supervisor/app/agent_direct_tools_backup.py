# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.readonly_context import ReadonlyContext

from app.shared.model import model_instance
from app.shared.callbacks import before_agent_callback, create_after_model_callback
from app.app_utils import helpers

# Import modular sub-agents
from app.agents.document_retriever.agent import document_retriever_agent
from app.agents.document_validator.agent import document_validator_agent
from app.agents.credit_checker.agent import credit_checker_agent
from app.agents.risk_assessor.agent import risk_assessor_agent
from app.agents.summarization_agent.agent import summarization_agent


# ==============================================================================
# 1. Additional Flow Function Tools
# ==============================================================================

def get_unprocessed_applications(limit: int = 5) -> str:
    """
    Retrieves the latest X unprocessed mortgage loan applications from the pending queue.

    Args:
        limit: The maximum number of applications to retrieve (default: 5).

    Returns:
        A formatted string containing the details of the unprocessed applications.
    """
    try:
        path = "/Users/gvarelal/Documents/demos/gartner/pending_applications.md"
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Parse the applications (delimited by "### Application ")
        sections = content.split("### Application ")
        header = sections[0]
        apps = sections[1:limit + 1]
        
        result = header
        for app in apps:
            result += "### Application " + app
            
        return result
    except Exception as e:
        return f"Error reading unprocessed applications: {str(e)}"


def summarize_batch_processing() -> str:
    """
    Summarizes the loan applications processed in the last batch by retrieving
    operational metrics, risk distributions, and strategic recommendations from the report.

    Returns:
        A formatted string with the summary of the last processed batch.
    """
    try:
        path = "/Users/gvarelal/Documents/demos/gartner/loan_processing_report.md"
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading batch processing summary: {str(e)}"


# ==============================================================================
# 2. Master Orchestrator Agent (loan_supervisor)
# ==============================================================================
async def _dynamic_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamically provides instructions to the agent by loading and formatting a prompt."""
    prompt = helpers.load_prompt_file_from_calling_agent()
    return prompt


loan_supervisor_agent = Agent(
    model=model_instance,
    name="loan_supervisor",
    description="A master orchestrator agent responsible for processing loan applications end-to-end, managing queues, and summarizing operations.",
    instruction=_dynamic_instruction_provider,
    tools=[
        AgentTool(document_retriever_agent),
        AgentTool(document_validator_agent),
        AgentTool(credit_checker_agent),
        AgentTool(risk_assessor_agent),
        AgentTool(summarization_agent),
        get_unprocessed_applications,
        summarize_batch_processing,
    ],
    before_agent_callback=before_agent_callback,
    after_model_callback=create_after_model_callback(agent_name="loan_supervisor"),
)

# Expose the app
app = App(
    root_agent=loan_supervisor_agent,
    name="app",
)
