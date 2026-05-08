import google.auth
from google.cloud import storage
from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

from app.shared.model import project, model_instance
from app.shared.callbacks import before_agent_callback, create_after_model_callback


def list_gcs_files(gcs_bucket_path: str) -> list[str]:
    """
    Lists all files in a Google Cloud Storage bucket path.

    Args:
        gcs_bucket_path: The full gs:// path, e.g., 'gs://my-bucket/applications/12345/'

    Returns:
        A list of full gs:// URIs for each file found.
    """
    try:
        if gcs_bucket_path.startswith("gs://"):
            path_without_scheme = gcs_bucket_path[5:]
        else:
            path_without_scheme = gcs_bucket_path

        parts = path_without_scheme.split("/", 1)
        bucket_name = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)

        file_paths = []
        for blob in blobs:
            if not blob.name.endswith("/"):
                file_paths.append(f"gs://{bucket_name}/{blob.name}")

        return file_paths
    except Exception as e:
        return [f"Error listing files: {str(e)}"]


# BigQuery Toolset Setup
credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bq_tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)
bq_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=bq_tool_config
)

from app.app_utils import helpers
from google.adk.agents.readonly_context import ReadonlyContext


def _dynamic_instruction_provider(context: ReadonlyContext) -> str:
    """Dynamically provides instructions to the agent by loading and formatting a prompt."""
    prompt = helpers.load_prompt_file_from_calling_agent(
        variables_to_replace={"project": project}
    )
    return prompt


document_retriever_agent = Agent(
    model=model_instance,
    name="Document_Retriever",
    description="Agent that retrieves GCS paths of documents for a given loan application ID by querying BigQuery and GCS.",
    instruction=_dynamic_instruction_provider,
    # tools=[bq_toolset, list_gcs_files],
    before_agent_callback=before_agent_callback,
    after_model_callback=create_after_model_callback(agent_name="document_retriever"),
)
