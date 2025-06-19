# Top GitHub Repositories (20k+ Stars) and Their Organization Websites

This project collects all GitHub repositories with at least **20,000 stars**, overcomes the GitHub Search API 1,000‑result limit by slicing queries, and then resolves each repository’s owner (user or organization) homepage URL. The final output is an Excel file linking repository names to their organization websites.

---

## 📂 Repository Structure

```
├── 1.py                    # Fetches all repos ≥ 20,000 stars (handles 1,000‑result cap)
├── 2.py                    # Fetches organization/user websites for each repo owner
├── all_top_repos.json      # Raw JSON list of all repos fetched by 1.py
├── org_websites.json       # JSON mapping repo full_name → owner → website (from 2.py)
├── final_output.xlsx       # Excel file generated from org_websites.json
├── workflow.pdf            # Description of project workflow and design decisions
└── README.md               # Project overview, setup instructions, and usage
```

---

## 🛠️ Prerequisites

* Python 3.8+
* GitHub Personal Access Token (PAT) with `repo` and `read:org` scopes

Install dependencies:

   ```bash
     pip install requests
   ```

---

## ⚙️ Setup

1. **Clone the repository**:

   ```bash
    git clone [https://github.com/JaishreeramCoder/top-starred-github-repos](https://github.com/yourusername/top-starred-github-repos)

    cd top-starred-repos

    ```

2. **Configure your GitHub token**:
   - Export as an environment variable:
    ```bash
        export GITHUB_TOKEN=your_personal_access_token
    ```

    - Or paste directly into `1.py` and `2.py` (not recommended).

---

## 🚀 Usage

### 1. Fetch All Top Repositories

```bash
python 1.py
```

* Queries the GitHub Search API in star‑range slices to bypass the 1,000‑result cap.
* Outputs `all_top_repos.json` containing a deduplicated list of repositories.

### 2. Fetch Organization Websites

```bash
python 2.py
```

* Reads `all_top_repos.json`, deduplicates owners, and calls `/orgs/{login}` or `/users/{login}`.
* Respects rate limits with retry after fixed delay.
* Outputs `org_websites.json` and `final_output.xlsx`.

---

## 📑 Workflow Overview

Please see [workflow.pdf](workflow.pdf) for detailed notes, but in summary:

1. **Initial Attempt**: Direct Search API call for `stars:>=20000` returned only 1,000 items due to GitHub’s cap.
2. **Range‑Slicing Strategy**: Iteratively split queries by star ranges, using the lowest star count in each batch to define the next slice.
3. **Deduplication**: Removed duplicate repos across overlapping star slices.
4. **Website Resolution**: The response from the fetch request to "api.github.com/search/repositories" doesn't provide us with the URL of the website of the owner, so separate API calls to user/org endpoints were necessary.
5. **Time Taken**: `1.py` took \~70 s, `2.py` took \~30 min due to per‑owner sequential requests.
6. **Data Export**: Final JSON and Excel files provide a clear mapping of top repos to organization websites.

---

## 🤝 Contributing

Feel free to open issues or submit pull requests for:

* Extending to other search filters (e.g., based on number of forks etc)
* Making requests at a certain fixed regular intervals and updating the final_output.xlsx accordingly in the repo

---

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.