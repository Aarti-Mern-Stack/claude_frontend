def fix_backend(client, task, repo_code):

    prompt = f"""
You are a senior backend developer.

Task:
{task}

Code:
{repo_code}

Return fixed code.
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text