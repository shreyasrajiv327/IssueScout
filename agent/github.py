import os
import requests


GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")

        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10"
        }

        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _get(self, endpoint, params=None):
        response = requests.get(
            f"{GITHUB_API}{endpoint}",
            headers=self.headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def get_open_issues(self, repository, since=None):
        params = {
            "state": "open",
            "sort": "created",
            "direction": "desc",
            "per_page": 100
        }

        if since:
            params["since"] = since

        issues = self._get(
            f"/repos/{repository}/issues",
            params
        )

        # GitHub's Issues API also returns PRs.
        # We only want actual issues.
        return [
            issue
            for issue in issues
            if "pull_request" not in issue
        ]

    def get_issue_comments(self, repository, issue_number):
        return self._get(
            f"/repos/{repository}/issues/{issue_number}/comments",
            {
                "per_page": 100
            }
        )

    def get_user_pull_requests(self, username, repository):
        result = self._get(
            "/search/issues",
            {
                "q": f"repo:{repository} is:pr author:{username}",
                "sort": "updated",
                "order": "desc",
                "per_page": 100
            }
        )

        return result.get("items", [])