# =============================================================================
# FILE: file_writer_tool.py
# PURPOSE:
#   Tools the pipeline agents use to save their work to the output/ folder.
#   `write_text_file` is complete and shows the pattern. You must finish
#   `write_html_file` and add at least ONE custom (non file-writer) tool.
# =============================================================================

import datetime
from pathlib import Path


# -----------------------------------------------------------------------------
# TOOL FUNCTION: write_text_file  (COMPLETE – use this as your reference)
# -----------------------------------------------------------------------------
def write_text_file(content: str, file_label: str) -> dict:
    """
    Writes a markdown document to a timestamped .md file in the output folder.

    Args:
        content (str): The full markdown document to save.
        file_label (str): Short snake_case label for the file name,
                          e.g. "market_research", "personas", "qa_review".

    Returns:
        dict: A dictionary containing the status and generated filename.
    """

    # Get the current date and time, format it as YYMMDD_HHMMSS.
    # Example: "250611_142317"
    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")

    # Keep the label safe for file names (letters, numbers, underscores only).
    safe_label = "".join(c if c.isalnum() or c == "_" else "_" for c in file_label.lower())

    # Example: "output/250611_142317_market_research.md"
    filename = f"output/{timestamp}_{safe_label}.md"

    # Ensure the "output" directory exists.
    Path("output").mkdir(exist_ok=True)

    try:
        Path(filename).write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "file": filename,
            "message": f"{safe_label} saved successfully."
        }

    except Exception as e:
        return {
            "status": "error",
            "file": filename,
            "message": f"Error: {str(e)}"
        }


# -----------------------------------------------------------------------------
# TOOL FUNCTION: write_html_file  (TODO)
# -----------------------------------------------------------------------------
def write_html_file(content: str) -> dict:
    """
    Writes a complete HTML page to a timestamped .html file in the output folder.

    Args:
        content (str): Full HTML document (including <!DOCTYPE html>) as a string.

    Returns:
        dict: A dictionary containing the status and generated filename.
    """

    # TODO: Follow the same pattern as write_text_file:
    #   1. build a timestamp
    #   2. filename = f"output/{timestamp}_landing_page.html"
    #   3. make sure output/ exists
    #   4. write the file inside try/except
    #   5. return a status dict
    return {"status": "error", "message": "write_html_file is not implemented yet"}


# -----------------------------------------------------------------------------
# CUSTOM TOOL  (TODO – at least one, NOT a file writer)
# -----------------------------------------------------------------------------
# Ideas (see ASSIGNMENT.md Section 5.2):
#   calculate_pricing(cost: float, margin_percent: float) -> dict
#   count_words(text: str) -> dict
#   check_html(html: str) -> dict
#   get_today() -> dict
#
# Rules:
#   - Type hints on every argument and the return value.
#   - A clear docstring (ADK sends it to the model as the tool description).
#   - Return a dict.
#   - Attach it to an agent with tools=[...] and tell the agent in
#     instructions.txt WHEN to call it.
