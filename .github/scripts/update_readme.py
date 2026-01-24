import requests
import re
import os

USERNAME = "nicovlr"
README_PATH = "README.md"

def get_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos"
    params = {"sort": "updated", "per_page": 100}
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def get_repo_languages(repo_name, headers):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return list(response.json().keys())
    return []

def generate_projects_table(repos):
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    projects = [r for r in repos if r["name"] != USERNAME and not r["fork"]]
    if not projects:
        return "*Aucun projet public pour l'instant*"

    projects = projects[:6]
    rows = []
    for repo in projects:
        name = repo["name"]
        url = repo["html_url"]
        description = repo["description"] or "—"
        languages = get_repo_languages(name, headers)
        lang_str = " · ".join(f"`{l}`" for l in languages[:3]) if languages else "—"
        rows.append(f"| [{name}]({url}) | {description[:50]}{'...' if len(description) > 50 else ''} | {lang_str} |")

    table = "| Projet | Description | Stack |\n"
    table += "|:-------|:------------|:------|\n"
    table += "\n".join(rows)
    return table

def update_readme(content):
    with open(README_PATH, "r") as f:
        readme = f.read()
    pattern = r"(<!-- PROJECTS:START -->)[\s\S]*(<!-- PROJECTS:END -->)"
    replacement = f"\\1\n{content}\n\\2"
    new_readme = re.sub(pattern, replacement, readme)
    with open(README_PATH, "w") as f:
        f.write(new_readme)

def main():
    print("Fetching repos...")
    repos = get_repos()
    if isinstance(repos, dict) and "message" in repos:
        print(f"Error: {repos['message']}")
        return
    print(f"Found {len(repos)} repos")
    print("Generating projects table...")
    table = generate_projects_table(repos)
    print("Updating README...")
    update_readme(table)
    print("Done!")

if __name__ == "__main__":
    main()
