"""
MCP Server implementation for HEP programming hints.

This module implements an MCP server using FastMCP that exposes tools
for accessing programming hints about HEP analysis libraries.
"""

import os
from pathlib import Path

from fastmcp import FastMCP

from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

assert "TOKEN" in os.environ, "Token needed for StaticTokenVerifier to control access to server"
# Define development tokens and their associated claims
verifier = StaticTokenVerifier(
    tokens={
        os.environ['TOKEN']: {
            "client_id": "guest-user",
            "scopes": ["read:data"]
        }
    },
    required_scopes=["read:data"]
)

app = FastMCP(name="hep-programming-hints", auth=verifier)

# Get the base directory (parent of hep_programming package)
BASE_DIR = Path(__file__).parent.parent
HINTS_DIR = BASE_DIR / "hints"

@app.tool()
def hep_coding_guidelines():
    """
    Provide high level context for generating HEP plots
    """
    hint_file = HINTS_DIR / "general.md"
    return hint_file.read_text()

@app.tool()
def get_hint(library: str) -> str:
    """
    Get programming hints for a specific HEP library.
    Common libraries used in analysing HEP data:
        servicex to fetch data from `rucio` datasets on the GRID, skimming out only the data required from the events needed.

        xaod hints to help with accessing ATLAS xAOD objects.

        awkward to perform operations on complicated arrays

        hist to generate histograms

        vector allows you to do 4-vector operations, transformation, calculations (like `deltaR`) easily and efficiently.

    Args:
        library: The library name (e.g., 'awkward', 'hist', 'servicex', 'vector', 'xaod')

    Returns:
        The content of the hints file for the requested library

    Raises:
        FileNotFoundError: If the hints file doesn't exist
    """
    # Normalize library name
    library_lower = library.lower()

    # Try to find the hints file
    hint_file = HINTS_DIR / f"{library_lower}-hints.md"

    if not hint_file.exists():
        # Try without the -hints suffix
        hint_file = HINTS_DIR / f"{library_lower}.md"

    if not hint_file.exists():
        available_files = [f.stem for f in HINTS_DIR.glob("*.md")]
        raise FileNotFoundError(
            f"No hints file found for '{library}'. "
            f"Available libraries: {', '.join(sorted(available_files))}"
        )

    return hint_file.read_text()


@app.tool()
def list_available_hints() -> str:
    """
    List all available hint files.

    Returns:
        A formatted string listing all available hint files
    """
    if not HINTS_DIR.exists():
        return "Hints directory not found"

    hint_files = sorted(HINTS_DIR.glob("*.md"))

    if not hint_files:
        return "No hint files available"

    result = ["Available HEP Programming Hints:\n"]

    for hint_file in hint_files:
        # Extract library name from filename
        name = hint_file.stem
        result.append(f"  - {name}")

    return "\n".join(result)

@app.tool()
def search_hints(keyword: str) -> str:
    """
    Search for a keyword across all hint files.

    Args:
        keyword: The keyword to search for

    Returns:
        A formatted string with files containing the keyword and context
    """
    if not HINTS_DIR.exists():
        return "Hints directory not found"

    keyword_lower = keyword.lower()
    results = []

    for hint_file in HINTS_DIR.glob("*.md"):
        content = hint_file.read_text()
        lines = content.split("\n")

        matches = []
        for i, line in enumerate(lines):
            if keyword_lower in line.lower():
                # Get context (line before and after if available)
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = "\n".join(lines[start:end])
                matches.append((i + 1, context))

        if matches:
            result = [f"\n## {hint_file.stem}\n"]
            for line_num, context in matches[:3]:  # Limit to first 3 matches per file
                result.append(f"Line {line_num}:\n```\n{context}\n```\n")
            results.append("\n".join(result))

    if not results:
        return f"No matches found for '{keyword}'"

    return f"Found '{keyword}' in {len(results)} file(s):\n" + "\n".join(results)


if __name__ == "__main__":
    # Run the MCP server
    app.run(transport="http", host="0.0.0.0", port=8080)
