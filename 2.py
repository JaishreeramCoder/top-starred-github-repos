import os
import json
import time
import requests
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout

# --- Configuration ---
# You can either set your GitHub Personal Access Token as an environment variable:
#    export GITHUB_TOKEN=your_token
# Or paste it directly below (not recommended for production):
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("Please set the GITHUB_TOKEN environment variable with your GitHub Personal Access Token.")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Load the list of repositories from all_top_repo.json
with open('all_top_repos.json', 'r') as f:
    repos = json.load(f)

output = []

# Helper: make a GET request with retries and exponential backoff
def get_with_retries(url, headers, max_retries=3, backoff_factor=1.0, timeout=10):
    """
    Performs HTTP GET with retry on connection issues.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, Timeout) as e:
            print(f"Attempt {attempt}: Connection issue for {url}: {e}")
        except HTTPError as e:
            # For HTTP errors (4xx, 5xx), break since retries unlikely to succeed
            print(f"HTTP error for {url}: {e}")
            break
        except RequestException as e:
            print(f"Request failed for {url}: {e}")
            break

        sleep_time = backoff_factor * (2 ** (attempt - 1))
        time.sleep(sleep_time)
    return None

for repo in repos:
    owner_info = repo.get('owner', {})
    owner_login = owner_info.get('login')
    owner_type = owner_info.get('type')  # 'Organization' or 'User'

    # Determine endpoint
    if owner_type == 'Organization':
        owner_api = f"https://api.github.com/orgs/{owner_login}"
    else:
        owner_api = f"https://api.github.com/users/{owner_login}"

    owner_data = get_with_retries(owner_api, HEADERS)

    if not owner_data:
        print(f"Failed to fetch data for owner: {owner_login}")
        website = None
    else:
        # 'blog' often holds the website, else fallback to HTML profile
        website = owner_data.get('blog') or owner_data.get('html_url')

    output.append({
        'repo_full_name': repo.get('full_name'),
        'owner': owner_login,
        'owner_type': owner_type,
        'website': website
    })

    # Brief pause to respect rate limits
    time.sleep(0.5)

# Save the results
with open('org_websites.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Done. Results saved to org_websites.json")
