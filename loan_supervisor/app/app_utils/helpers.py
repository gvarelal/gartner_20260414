import os
import pathlib
import traceback
import json
import enum
import inspect
import json
import sys
from typing import Optional


def load_prompt_file_from_calling_agent(
    variables_to_replace: dict[str, str] | None = None,
    filename: str | None = None,
) -> str:
    """Loads and optionally formats a 'prompt.md' file from the calling agent's directory.

    This utility function is designed to be called by an agent to dynamically
    load its associated prompt file. It inspects the call stack to determine
    the caller's file path, constructs the path to 'prompt.md' relative to
    that caller, and if provided, replaces placeholders in the format `{{key}}`
    with values from the `variables_to_replace` dictionary.

    Args:
        variables_to_replace: An optional dictionary where keys are placeholder
            names (without curly braces) and values are the strings to
            substitute.
        filename: Optional name of the file to load. Defaults to 'prompt.md'.

    Returns:
        The content of the 'prompt.md' file, with placeholders replaced if a
        dictionary was provided.

    Raises:
        FileNotFoundError: If 'prompt.md' is not found in the caller's directory.
        ValueError: If the loaded prompt is empty.
    """
    caller_frame = inspect.stack()[1]
    caller_filepath = pathlib.Path(caller_frame.filename)
    caller_dir = caller_filepath.parent
    filename = filename or "prompt.md"
    prompt = ""

    try:

        local_prompts_path = (caller_dir / filename).resolve()
        with open(local_prompts_path, "r", encoding="utf-8") as file:
            prompt = file.read()

        if not prompt:
            raise ValueError("Prompt is empty or could not be loaded.")

        modified_prompt = prompt
        if variables_to_replace:
            for key, value in variables_to_replace.items():
                if value is None:
                    raise ValueError(
                        f"Prompt value replacement for key '{key}' is empty."
                    )
                placeholder = "{{" + key + "}}"
                modified_prompt = modified_prompt.replace(placeholder, str(value))

        log_message(
            f"Prompt loaded correctly. Agent: {caller_filepath}.", Severity.INFO
        )
        return modified_prompt
    except FileNotFoundError as e:
        log_message(
            f"ERROR. Prompt file not found. Agent: {caller_filepath}. Error: {e}",
            Severity.ERROR,
        )
        traceback.print_exc()
        raise
    except ValueError as e:
        log_message(
            f"ERROR. An error occurred while loading prompt. Agent: {caller_filepath}. Error: {e}",
            Severity.ERROR,
        )
        traceback.print_exc()
        raise
    except Exception as e:
        log_message(
            f"ERROR. An error occurred while loading prompt. Agent: {caller_filepath}. Error: {e}",
            Severity.ERROR,
        )
        traceback.print_exc()
        raise


class Severity(enum.Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


def log_message(message: str, severity: Severity, prefix: Optional[str] = None):
    """Logs a message with a severity and optional prefix.

    Args:
        message: The message to log.
        severity: The severity of the log (DEBUG, INFO, ERROR).
        prefix: Optional prefix. If None, attempts to auto-detect from call stack.
    """
    if prefix is None:
        try:
            # Auto-detect prefix from caller
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_frame = frame.f_back

                # Try to get class name
                cls_name = ""
                if "self" in caller_frame.f_locals:
                    cls_name = caller_frame.f_locals["self"].__class__.__name__
                elif "cls" in caller_frame.f_locals:
                    cls_name = caller_frame.f_locals["cls"].__name__

                func_name = caller_frame.f_code.co_name

                if cls_name:
                    prefix = f"{cls_name}.{func_name}"
                else:
                    prefix = func_name
        except Exception:
            prefix = "Unknown"

    caller_file = "Unknown"
    caller_line = 0
    try:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_frame = frame.f_back
            caller_file = caller_frame.f_code.co_filename
            caller_line = caller_frame.f_lineno
    except Exception:
        pass

    log_payload = {
        "severity": severity.name,
        "message": message,
        "logging.googleapis.com/sourceLocation": {
            "file": caller_file,
            "line": caller_line,
            "function": prefix or "Unknown",
        },
        "prefix": prefix,
        "version": get_required_env_var("AGENT_VERSION"),
    }
    log_str = json.dumps(log_payload)
    if severity == Severity.ERROR:
        print(log_str, file=sys.stderr)
    else:
        print(log_str, file=sys.stdout)


def get_required_env_var(var_name: str) -> str:
    """Gets a required environment variable or raises a clear exception."""
    from dotenv import load_dotenv

    load_dotenv()
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(
            f"Environment variable '{var_name}' is missing and is required."
        )
    return value
