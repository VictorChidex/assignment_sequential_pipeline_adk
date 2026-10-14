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


# -----------------------------------------------------------------------------
# TOOL FUNCTION: write_html_file
# -----------------------------------------------------------------------------
def write_html_file(content: str) -> dict:
    """
    Writes a complete HTML page to a timestamped HTML file.

    Args:
        content (str): Full HTML document, including <!DOCTYPE html>.

    Returns:
        dict: The status, generated filename, and message.
    """

    if not isinstance(content, str) or not content.strip():
        return {
            "status": "error",
            "file": None,
            "message": "Error: content must be a non-empty HTML string."
        }

    filename = None

    try:
        timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S_%f")
        filename = f"output/{timestamp}_landing_page.html"

        Path("output").mkdir(parents=True, exist_ok=True)
        Path(filename).write_text(content, encoding="utf-8")

        return {
            "status": "success",
            "file": str(Path(filename).resolve()),
            "message": "HTML page saved successfully."
        }

    except Exception as e:
        return {
            "status": "error",
            "file": filename,
            "message": f"Error: {type(e).__name__}: {str(e)}"
        }



    # TODO: Follow the same pattern as write_text_file:
    #   1. build a timestamp
    #   2. filename = f"output/{timestamp}_landing_page.html"
    #   3. make sure output/ exists
    #   4. write the file inside try/except
    #   5. return a status dict
    #   return {"status": "error", "message": "write_html_file is not implemented yet"}



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


import math

def calculate_pricing(cost: float, margin_percent: float) -> dict:
    """
    Calculates selling price based on cost and desired profit margin.

    Args:
        cost (float): Product cost; must be non-negative.
        margin_percent (float): Profit margin as a percentage of selling price,
            from 0 to below 100.

    Returns:
        dict: A dictionary containing the status, pricing details, and message.
    """

    try:
        # Ensure the cost is finite and non-negative.
        if not math.isfinite(cost) or cost < 0:
            raise ValueError("Cost must be finite and non-negative.")

        # Ensure the profit margin is within the valid range.
        if not math.isfinite(margin_percent) or not 0 <= margin_percent < 100:
            raise ValueError("Margin percentage must be between 0 and below 100.")

        # Calculate the selling price and profit.
        selling_price = cost / (1 - margin_percent / 100)
        profit = selling_price - cost

        return {
            "status": "success",
            "cost": round(cost, 2),
            "margin_percent": margin_percent,
            "selling_price": round(selling_price, 2),
            "profit": round(profit, 2),
            "message": "Pricing calculated successfully."
        }

    except (TypeError, ValueError, OverflowError) as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }



import datetime
import re
from html.parser import HTMLParser


def count_words(text: str) -> dict:
    """
    Counts the words in the provided text.

    Args:
        text (str): The text to count words in.

    Returns:
        dict: A dictionary containing the status, word count, and message.
    """

    try:
        # Ensure the input is a string.
        if not isinstance(text, str):
            raise TypeError("Text must be a string.")

        # Count whitespace-separated words.
        word_count = len(text.split())

        return {
            "status": "success",
            "word_count": word_count,
            "message": "Words counted successfully."
        }

    except (TypeError, ValueError) as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


def check_html(html: str) -> dict:
    """
    Checks a complete HTML document for basic structural elements.
    This is a basic check, not a full HTML standards validator.

    Args:
        html (str): Full HTML document (including <!DOCTYPE html>) as a string.

    Returns:
        dict: A dictionary containing the status, check result, and message.
    """

    class DocumentParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.opening_tags = set()
            self.closing_tags = set()
            self.has_doctype = False

        def handle_decl(self, decl):
            if decl.strip().lower() == "doctype html":
                self.has_doctype = True

        def handle_starttag(self, tag, attrs):
            self.opening_tags.add(tag)

        def handle_endtag(self, tag):
            self.closing_tags.add(tag)

    try:
        # Ensure the input is a non-empty string.
        if not isinstance(html, str):
            raise TypeError("HTML must be a string.")

        if not html.strip():
            raise ValueError("HTML must not be empty.")

        # Parse the document to identify structural elements.
        parser = DocumentParser()
        parser.feed(html)
        parser.close()

        # Check for the doctype and required opening and closing tags.
        missing_elements = []

        if not parser.has_doctype:
            missing_elements.append("<!DOCTYPE html>")

        for tag in ("html", "head", "body"):
            if tag not in parser.opening_tags:
                missing_elements.append(f"<{tag}>")
            if tag not in parser.closing_tags:
                missing_elements.append(f"</{tag}>")

        passed = not missing_elements

        return {
            "status": "success",
            "passes_basic_checks": passed,
            "missing_elements": missing_elements,
            "message": (
                "HTML passed basic structural checks."
                if passed
                else "HTML is missing required structural elements."
            )
        }

    except (TypeError, ValueError) as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


def get_today() -> dict:
    """
    Gets today's date using the system's local timezone.

    Args:
        None.

    Returns:
        dict: A dictionary containing the status, current date, and message.
    """

    try:
        # Get today's date.
        today = datetime.date.today()

        return {
            "status": "success",
            "date": today.isoformat(),
            "day": today.strftime("%A"),
            "message": "Today's date retrieved successfully."
        }

    except (ValueError, OSError) as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }