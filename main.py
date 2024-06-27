import httpx
import time
import json
import sys
import datetime
import pathlib
from markdown_it import MarkdownIt

md = MarkdownIt("gfm-like")
here = pathlib.Path(".") / "issues"
here.mkdir(exist_ok=True)
last_run = None
if (here / "last_run").exists():
  with open(here / "last_run") as f:
    last_run = f.read().strip()

with open(here / "last_run", "w") as f:
  f.write(str(datetime.datetime.now(datetime.timezone.utc).isoformat()))

TOKEN = ""

if TOKEN:
  headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
  }
else:
  headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
  }

def issues(*, sleep_for = 1.0):
  next_links = ["https://api.github.com/repos/python/mypy/issues?per_page=100"]

  if last_run:
    next_links[0] = next_links[0] + f"&since={last_run}"

  result = []

  while next_links:
    assert len(next_links) == 1
    print(f"fetching {next_links[0]}", file=sys.stderr)
    r = httpx.get(next_links[0], headers=headers)
    r.raise_for_status()
    next_links = [h.removesuffix('; rel="next"').strip("<>") for h in r.headers.get("link", "").split(", ") if h.endswith('; rel="next"')]

    result.extend(r.json())
    if next_links:
      time.sleep(sleep_for)

  return [r for r in result if "pull_request" not in r]

for issue in issues():
  issue_dir = here / str(issue["number"])
  issue_dir.mkdir(exist_ok=True)

  next_links = [issue["comments_url"] + "?per_page=100"]
  comments = [issue["body"]]
  while next_links:
    assert len(next_links) == 1
    print(f"fetching {next_links[0]}", file=sys.stderr)
    r = httpx.get(next_links[0], headers=headers)
    r.raise_for_status()
    next_links = [h.removesuffix('; rel="next"').strip("<>") for h in r.headers.get("link", "").split(", ") if h.endswith('; rel="next"')]

    comments.extend([c["body"] for c in r.json()])
    time.sleep(1.0)

  blocks = []

  for comment in comments:
    for token in md.parse(comment):
      # TODO: check if it's not ```py, ```python, or ``` (basic filtering)
      if token.type == "fence" and token.tag == "code":
        blocks.append(token.content)

  with open(issue_dir / "blocks.json", "w") as f:
    f.write(json.dumps(blocks))

