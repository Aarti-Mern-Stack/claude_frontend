import os
import json
import subprocess
import anthropic
from github import Github, Auth
from tl_agent import analyze_issue
from frontend_agent import fix_frontend
from backend_agent import fix_backend
from qa_agent import review_code


def get_repo_code():
    """Read all source files from the src/ directory."""
    src_dir = os.path.join(os.path.dirname(__file__), "..", "src")
    code_parts = []
    for root, _dirs, files in os.walk(src_dir):
        for fname in sorted(files):
            if fname.endswith((".jsx", ".js", ".css")):
                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, os.path.join(src_dir, ".."))
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                code_parts.append(f"--- {rel_path} ---\n{content}")
    return "\n\n".join(code_parts)


def apply_code_changes(fix_output):
    """Ask Claude to produce file-level patches and apply them."""
    client = anthropic.Anthropic()
    src_dir = os.path.join(os.path.dirname(__file__), "..", "src")

    prompt = f"""
You are a code-apply assistant.

Given the following fix description, extract every file change as a JSON array.
Each element must have:
  "file": relative path from the project root (e.g. "src/pages/Login.jsx"),
  "content": the full updated file content.

Only include files that need changes. Return ONLY valid JSON, no markdown fences.

Fix description:
{fix_output}
"""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    changes = json.loads(text)
    project_root = os.path.join(os.path.dirname(__file__), "..")

    for change in changes:
        filepath = os.path.join(project_root, change["file"])
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(change["content"])
        print(f"Updated: {change['file']}")


def main():
    issue_number = int(os.environ["ISSUE_NUMBER"])
    github_token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ.get("GITHUB_REPOSITORY", "")

    gh = Github(auth=Auth.Token(github_token))
    repo = gh.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

    print(f"Processing issue #{issue_number}: {issue.title}")

    client = anthropic.Anthropic()
    repo_code = get_repo_code()

    # Step 1: TL agent analyzes the issue
    analysis = analyze_issue(client, issue.title, issue.body or "")
    print(f"TL Analysis: {analysis}")

    # Step 2: Route to the right developer agent
    if "frontend" in analysis.lower():
        fix = fix_frontend(client, analysis, repo_code)
    elif "backend" in analysis.lower():
        fix = fix_backend(client, analysis, repo_code)
    else:
        fix = fix_frontend(client, analysis, repo_code)

    # Step 3: QA review
    qa_result = review_code(client, fix)
    print(f"QA Result: {qa_result}")

    # Step 4: Apply changes and create PR
    apply_code_changes(fix)

    branch_name = f"ai-fix-{issue_number}"
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"AI fix for issue #{issue_number}"],
        check=True,
    )
    subprocess.run(["git", "push", "origin", branch_name], check=True)

    pr = repo.create_pull(
        title=f"AI fix for issue #{issue_number}",
        body=(
            f"Closes #{issue_number}\n\n"
            f"**TL Analysis:**\n{analysis}\n\n"
            f"**QA Review:**\n{qa_result}\n\n"
            "This PR was generated automatically by the AI agent pipeline."
        ),
        head=branch_name,
        base="main",
    )

    print(f"Pull request created: {pr.html_url}")
    issue.create_comment(
        f"AI fix has been proposed in PR #{pr.number}: {pr.html_url}"
    )


if __name__ == "__main__":
    main()
