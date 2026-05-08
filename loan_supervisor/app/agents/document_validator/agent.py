import asyncio
import mimetypes
from google import genai
from google.genai import types
from google.adk.agents import Agent

from app.shared.model import model_instance
from app.shared.callbacks import before_agent_callback, create_after_model_callback

client = genai.Client(vertexai=True, location="global")


def parse_gcs_document(gcs_uri: str) -> str:
    """
    Spawns the doc_parser sub-agent to analyze a document stored in GCS.

    Args:
        gcs_uri: The full gs:// URI of the document to parse (e.g., gs://bucket/file.pdf).

    Returns:
        A structured string containing the extracted fields and insights.
    """
    mime_type, _ = mimetypes.guess_type(gcs_uri)
    if not mime_type:
        mime_type = "application/octet-stream"
        if gcs_uri.endswith(".pdf"):
            mime_type = "application/pdf"
        elif gcs_uri.endswith(".jpg") or gcs_uri.endswith(".jpeg"):
            mime_type = "image/jpeg"
        elif gcs_uri.endswith(".png"):
            mime_type = "image/png"
        elif gcs_uri.endswith(".json"):
            mime_type = "application/json"

    try:
        document_part = types.Part.from_uri(file_uri=gcs_uri, mime_type=mime_type)

        parsing_instruction = """
        You are the doc_parser sub-agent.
        Your task is to analyze the provided document content and extract relevant information for assessing the eligibility of the applicant for a loan.
        
        1. Understand the document type. It can be one of: Driver's License, Tax Statement, Pay stub, Loan Application.
        2. Extract the following relevant fields based on the document type:
           - Driver's License: Name, Address, DOB, Expiry.
           - Tax Statement: Year, Tax Paid, Taxable Income.
           - Pay stub: Hourly Pay, Pay Period, Salary of the period, YTD Pay.
           - Loan Application: Call out if any of the following mandatory fields are missing: Name, Phone, Email, Employment Status, Address, SSN. Also extract the ones that are present.
         3. Document any additional insights you find while looking at the document beyond the required fields.
        
        Format your response clearly, stating the Document Type first, then the Extracted Fields, and finally any Additional Insights. Do not redact any PII information like SSN since it will used for verification in the next steps. If you find any discrepancies / mismatches in common fields (like address, SSN) across documents, call it out. Also in the response ask the user if they would like to proceed to the next step.
        """

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[document_part, parsing_instruction],
        )
        return response.text or "No content generated."
    except Exception as e:
        return f"Failed to parse document {gcs_uri}. Error: {str(e)}"


async def parse_multiple_documents(gcs_uris: list[str]) -> str:
    """
    Parses multiple documents in parallel using the parse_gcs_document tool.

    Args:
        gcs_uris: A list of full gs:// URIs of the documents to parse.

    Returns:
        A consolidated string containing the extraction results for all documents.
    """
    tasks = [asyncio.to_thread(parse_gcs_document, uri) for uri in gcs_uris]
    results = await asyncio.gather(*tasks)

    consolidated_response = ""
    for uri, result in zip(gcs_uris, results):
        consolidated_response += f"### Document: {uri}\n\n{result}\n\n---\n\n"

    return consolidated_response


from app.app_utils import helpers
from google.adk.agents.readonly_context import ReadonlyContext


def _dynamic_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamically provides instructions to the agent by loading and formatting a prompt."""
    prompt = helpers.load_prompt_file_from_calling_agent()
    return prompt


document_validator_agent = Agent(
    model=model_instance,
    name="Document_Validator",
    description="Agent that coordinates parsing and validating a list of GCS documents.",
    instruction=_dynamic_instruction_provider,
    # tools=[parse_multiple_documents],
    before_agent_callback=before_agent_callback,
    after_model_callback=create_after_model_callback(agent_name="document_validator"),
)
