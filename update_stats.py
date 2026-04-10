import os
import re
import requests

USERNAME = os.environ.get("USER_NAME", "amalsom10")
TOKEN    = os.environ.get("ACCESS_TOKEN", "")

headers = {"Authorization": f"bearer {TOKEN}"} if TOKEN else {}

print(f"Fetching stats for {USERNAME}...")

# ── REST: basic user info ──────────────────────────────────────
user = requests.get(
    f"https://api.github.com/users/{USERNAME}",
    headers=headers,
).json()

public_repos = user.get("public_repos", "--")
followers    = user.get("followers", "--")

# ── REST: total stars across all repos ────────────────────────
stars = 0
page  = 1
while True:
    repos = requests.get(
        f"https://api.github.com/users/{USERNAME}/repos",
        params={"per_page": 100, "page": page},
        headers=headers,
    ).json()
    if not repos or not isinstance(repos, list):
        break
    stars += sum(r.get("stargazers_count", 0) for r in repos)
    if len(repos) < 100:
        break
    page += 1

# ── GraphQL: total commit contributions ───────────────────────
commits = "--"
if TOKEN:
    query = """
    {
      user(login: "%s") {
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """ % USERNAME
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers={"Authorization": f"bearer {TOKEN}"},
    )
    data = resp.json().get("data", {})
    cc   = data.get("user", {}).get("contributionsCollection", {})
    commits = (
        cc.get("totalCommitContributions", 0)
        + cc.get("restrictedContributionsCount", 0)
    )

print(f"repos={public_repos}  stars={stars}  commits={commits}  followers={followers}")

# ── Update SVGs ───────────────────────────────────────────────
for fname in ["dark_mode.svg", "light_mode.svg"]:
    with open(fname) as f:
        svg = f.read()

    svg = svg.replace("REPO_COUNT",     str(public_repos))
    svg = svg.replace("STAR_COUNT",     str(stars))
    svg = svg.replace("COMMIT_COUNT",   str(commits))
    svg = svg.replace("FOLLOWER_COUNT", str(followers))

    with open(fname, "w") as f:
        f.write(svg)
    print(f"Updated {fname}")

print("Done.")
