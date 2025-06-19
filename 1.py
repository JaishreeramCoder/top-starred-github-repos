import os
import json
import requests

# Use your environment variable for security, fallback to hardcoded token if absent
TOKEN = os.getenv(
    "GITHUB_TOKEN"
)
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}
BASE_URL = "https://api.github.com/search/repositories"


def fetch_range(min_stars, max_stars=None):
    """
    Fetch all repos with stars between min_stars and max_stars (inclusive), following pagination links.
    If max_stars is None, fetch repos with stars >= min_stars.
    """
    repos = []
    url = BASE_URL
    q = f"stars:>={min_stars}" if max_stars is None else f"stars:{min_stars}..{max_stars}"
    params = {"q": q, "sort": "stars", "order": "desc", "per_page": 100}

    while url:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        repos.extend(items)

        # If fewer than a full page, no more pages
        if len(items) < 100:
            break

        # Parse Link header for next page
        link = resp.headers.get("Link", "")
        next_url = None
        for part in link.split(','):
            if 'rel="next"' in part:
                next_url = part[part.find('<')+1:part.find('>')]
                break

        url = next_url
        params = None  # subsequent requests have URL fully defined

    return repos


def fetch_all(min_stars=20_000):
    """
    Fetch all repositories with star count >= min_stars by recursively narrowing star ranges.
    Uses max = lowest_star to include ties, then deduplicates at the end.
    Returns de-duplicated list of repos sorted by star count descending.
    """
    all_repos = {}
    current_min = min_stars
    current_max = None

    while True:
        print(f"Fetching repos with stars >= {current_min}" + (f" and <= {current_max}" if current_max else ""))
        items = fetch_range(current_min, current_max)
        if not items:
            break

        # Add/update entries to dedupe by full_name
        for repo in items:
            all_repos[repo["full_name"]] = repo

        # If under 1000, we've fetched all of this slice
        if len(items) < 1000:
            break

        # Otherwise, determine new upper bound at the lowest-starred repo (include ties)
        lowest = items[-1]["stargazers_count"]
        current_max = lowest

    # Convert to list and sort
    result = list(all_repos.values())
    result.sort(key=lambda r: r["stargazers_count"], reverse=True)
    return result


if __name__ == "__main__":
    repos = fetch_all(min_stars=20_000)
    print(f"Total repos fetched: {len(repos)}")
    # Save full data to JSON
    outfile = "all_top_repos.json"
    with open(outfile, "w") as f:
        json.dump(repos, f, indent=2)
    print(f"Saved {len(repos)} repositories to {outfile}")
