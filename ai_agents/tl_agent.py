import anthropic

def analyze_issue(client, issue_title, issue_body):

    prompt = f"""
You are a tech lead.

Analyze this GitHub issue and decide:
1. Is this a frontend or backend problem?
2. What task should developer perform?

Issue title:
{issue_title}

Issue description:
{issue_body}

Return JSON:
{{
 "type": "frontend or backend",
 "task": "what needs to be fixed"
}}
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text