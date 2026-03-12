"""
AI agent that reads a GitHub issue and suggests a fix for frontend bugs.
Runs inside GitHub Actions, triggered when a new issue is opened.
"""

import os
import sys
from pathlib import Path

from github import Github
from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")  # owner/repo
ISSUE_NUMBER = os.environ.get("ISSUE_NUMBER")

FRONTEND_DIRS = ["src", "components", "pages", "hooks"]
FRONTEND_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".css", ".html"}
MAX_FILE_SIZE = 30_000  # characters per file – keep context manageable


def validate_env():
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not GITHUB_TOKEN:
        missing.append("GITHUB_TOKEN")
    if not GITHUB_REPOSITORY:
        missing.append("GITHUB_REPOSITORY")
    if not ISSUE_NUMBER:
        missing.append("ISSUE_NUMBER")
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# GitHub helpers
# ---------------------------------------------------------------------------
def fetch_issue():
    """Return the issue object for the triggering issue number."""
    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(GITHUB_REPOSITORY)
    issue = repo.get_issue(number=int(ISSUE_NUMBER))
    return issue


# ---------------------------------------------------------------------------
# Codebase helpers
# ---------------------------------------------------------------------------
def collect_frontend_files():
    """Walk the frontend directories and return a dict of {path: content}."""
    repo_root = Path(".")
    files = {}

    for dir_name in FRONTEND_DIRS:
        dir_path = repo_root / dir_name
        if not dir_path.is_dir():
            continue
        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in FRONTEND_EXTENSIONS:
                continue
            if "node_modules" in file_path.parts:
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                if len(content) <= MAX_FILE_SIZE:
                    files[str(file_path)] = content
            except OSError:
                continue

    return files


def format_codebase(files: dict) -> str:
    """Format collected files into a single string for the prompt."""
    parts = []
    for path, content in sorted(files.items()):
        parts.append(f"--- {path} ---\n{content}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Claude analysis
# ---------------------------------------------------------------------------
def analyze_issue(issue_title: str, issue_body: str, codebase: str) -> str:
    """Send the issue + codebase to Claude and return the suggested fix."""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are a senior frontend engineer. A GitHub issue has been filed
against a React codebase. Your job is to:

1. Understand the bug or feature request described in the issue.
2. Identify which file(s) in the codebase are relevant.
3. Suggest a concrete fix — include the exact code changes (diffs or full
   replacement snippets) with file paths.
4. Briefly explain why the fix works.

## GitHub Issue

**Title:** {issue_title}

**Description:**
{issue_body}

## Codebase

{codebase}

Provide your answer in the following format:

### Analysis
<short description of the root cause>

### Files to change
<list of file paths>

### Suggested fix
<for each file, show the change as a code block with the file path>

### Explanation
<why this fixes the issue>
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    validate_env()

    print("Fetching GitHub issue …")
    issue = fetch_issue()
    print(f"Issue #{issue.number}: {issue.title}")

    print("Collecting frontend source files …")
    files = collect_frontend_files()
    print(f"Found {len(files)} file(s) across {FRONTEND_DIRS}")

    if not files:
        print("WARNING: No frontend files found. Check directory structure.")

    codebase = format_codebase(files)

    print("Sending issue and codebase to Claude for analysis …")
    suggestion = analyze_issue(
        issue_title=issue.title,
        issue_body=issue.body or "(no description provided)",
        codebase=codebase,
    )

    print("\n" + "=" * 72)
    print("AI-SUGGESTED FIX")
    print("=" * 72 + "\n")
    print(suggestion)


if __name__ == "__main__":
    main()
