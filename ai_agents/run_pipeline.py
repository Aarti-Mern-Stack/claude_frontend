import anthropic
from tl_agent import analyze_issue
from frontend_agent import fix_frontend
from backend_agent import fix_backend
from qa_agent import review_code

client = anthropic.Anthropic()

issue_title = "Login button not working"
issue_body = "Clicking login does nothing"

analysis = analyze_issue(client, issue_title, issue_body)

print("TL Analysis:", analysis)

if "frontend" in analysis.lower():

    code = fix_frontend(client, analysis, "repo code")

elif "backend" in analysis.lower():

    code = fix_backend(client, analysis, "repo code")

qa_result = review_code(client, code)

print("QA Result:", qa_result)