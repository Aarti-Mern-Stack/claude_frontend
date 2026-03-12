def fix_frontend(client, task, repo_code):

    prompt = f"""
You are a senior frontend developer.

Task:
{task}

Repository code:
{repo_code}

Fix the issue and return corrected code.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text