#!/usr/bin/env python3
"""Generate GitHub stats block and inject into README.md.
Requires: requests
Environment:
  GH_USERNAME - GitHub username
  GH_TOKEN - GitHub token with repo access (GITHUB_TOKEN in Actions)
  README_PATH - path to README (default: README.md)
"""
import os
import sys
import math
import re
import requests
from typing import Dict

GH_USERNAME = os.getenv("GH_USERNAME")
GH_TOKEN = os.getenv("GH_TOKEN")
README_PATH = os.getenv("README_PATH", "README.md")

API_BASE = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"

if not GH_USERNAME or not GH_TOKEN:
    print("GH_USERNAME and GH_TOKEN must be set", file=sys.stderr)
    sys.exit(2)

session = requests.Session()
session.headers.update({
    "Authorization": f"bearer {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "generate-readme-stats-script"
})

# Fetch public repos (paginated)
repos = []
page = 1
per_page = 100
while True:
    url = f"{API_BASE}/users/{GH_USERNAME}/repos"
    params = {"per_page": per_page, "page": page, "type": "owner", "sort": "full_name"}
    r = session.get(url, params=params)
    if r.status_code != 200:
        print(f"Failed to fetch repos: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(3)
    page_items = r.json()
    if not page_items:
        break
    repos.extend(page_items)
    if len(page_items) < per_page:
        break
    page += 1

# Filter public non-fork repositories
repos = [r for r in repos if not r.get("fork") and not r.get("private")]
repo_count = len(repos)

total_stars = sum(r.get("stargazers_count", 0) for r in repos)

# Aggregate languages
lang_totals: Dict[str, int] = {}
for r in repos:
    full_name = r.get("full_name")
    if not full_name:
        continue
    lr = session.get(f"{API_BASE}/repos/{full_name}/languages")
    if lr.status_code != 200:
        print(f"Failed to fetch languages for {full_name}: {lr.status_code} {lr.text}", file=sys.stderr)
        sys.exit(4)
    data = lr.json()
    for lang, bytes_count in data.items():
        lang_totals[lang] = lang_totals.get(lang, 0) + bytes_count

# Compute top 6 languages by bytes
total_bytes = sum(lang_totals.values())
lang_list = []
if total_bytes > 0:
    for lang, b in sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)[:6]:
        pct = (b / total_bytes) * 100
        lang_list.append((lang, b, pct))

# GraphQL: contributions and counts
graphql_query = '''
query($login:String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { totalContributions }
      totalCommitContributions
      totalRepositoryContributions
      totalIssueContributions
      totalPullRequestContributions
    }
    pullRequests { totalCount }
    issues { totalCount }
  }
}
'''
resp = session.post(GRAPHQL_URL, json={"query": graphql_query, "variables": {"login": GH_USERNAME}})
if resp.status_code != 200:
    print(f"GraphQL request failed: {resp.status_code} {resp.text}", file=sys.stderr)
    sys.exit(5)
j = resp.json()
if "errors" in j:
    print(f"GraphQL errors: {j['errors']}", file=sys.stderr)
    sys.exit(6)
user = j.get("data", {}).get("user") or {}
contribs = user.get("contributionsCollection", {})
commits_last_year = contribs.get("totalCommitContributions", 0)
contributions_last_year = contribs.get("contributionCalendar", {}).get("totalContributions", 0)
pr_count = user.get("pullRequests", {}).get("totalCount", 0)
issues_count = user.get("issues", {}).get("totalCount", 0)

# Build ASCII block
def bar(pct, width=24):
    filled = int(round((pct / 100.0) * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)

lines = []
lines.append(f"Repositories: {repo_count}")
lines.append(f"Total stars: {total_stars}")
lines.append(f"Commits (last year): {commits_last_year}")
lines.append(f"Contributions (last year): {contributions_last_year}")
lines.append(f"Pull requests: {pr_count}")
lines.append(f"Issues: {issues_count}")
lines.append("")
lines.append("Top languages:")
for lang, b, pct in lang_list:
    lines.append(f"- {lang.ljust(12)} {pct:5.1f}% |{bar(pct)}|")

block = "\n".join(lines)
md_block = "<!--STATS:START-->\n```text\n" + block + "\n```\n<!--STATS:END-->"

# Read README and replace between markers
try:
    with open(README_PATH, "r", encoding="utf-8") as fh:
        content = fh.read()
except FileNotFoundError:
    print(f"README not found at {README_PATH}", file=sys.stderr)
    sys.exit(7)

# Safely replace only between exact markers using string indices
start_marker = "<!--STATS:START-->"
end_marker = "<!--STATS:END-->"
start_idx = content.find(start_marker)
if start_idx != -1:
    end_idx = content.find(end_marker, start_idx)
    if end_idx != -1:
        # Replace entire marker block with generated md_block
        new_content = content[:start_idx] + md_block + content[end_idx + len(end_marker):]
    else:
        # No end marker found: append md_block at end
        if not content.endswith("\n"):
            content += "\n"
        new_content = content + "\n" + md_block + "\n"
else:
    # markers not present: append md_block at end
    if not content.endswith("\n"):
        content += "\n"
    new_content = content + "\n" + md_block + "\n"

if new_content == content:
    print("No changes required.")
    sys.exit(0)

with open(README_PATH, "w", encoding="utf-8") as fh:
    fh.write(new_content)

print("README updated with generated stats.")
sys.exit(0)
