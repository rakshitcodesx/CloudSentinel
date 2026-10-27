# cloudsentinel/integrations/github.py
import os
import httpx

def post_pr_comment(repo: str, pr_number: int, comment_body: str) -> dict:
    """
    Posts a review comment to a GitHub Pull Request using the GitHub REST API.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is missing. Cannot post to GitHub.")
        
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = httpx.post(url, headers=headers, json={"body": comment_body})
    response.raise_for_status()
    
    return {"status": "success", "comment_url": response.json().get("html_url")}
