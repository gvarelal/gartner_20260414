import os
import google.auth
from google import genai
from google.adk.models import Gemini

# --- Common Setup ---
_, project_id = google.auth.default()
project = os.environ.get("GOOGLE_CLOUD_PROJECT", project_id or "demo4events10")

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = project
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

model_instance = Gemini(model="gemini-3.1-flash-lite")
