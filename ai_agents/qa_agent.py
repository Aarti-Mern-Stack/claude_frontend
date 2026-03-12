def review_code(client, code):

    prompt = f"""
You are a QA engineer.

Review this code and check if the issue is fixed.

Code:
{code}

Return:
PASS  (if correct)

or

FIX_REQUIRED
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text