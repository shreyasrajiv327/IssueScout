import json
from datetime import datetime, timedelta, timezone

from github import GitHubClient


def main():
    with open("config/config.example.json") as f:
        config = json.load(f)

    github = GitHubClient()

    since = datetime.now(timezone.utc) - timedelta(hours=24)

    for repository in config["repositories"]:

        print(f"\nRepository: {repository}")
        print("-" * 60)

        issues = github.get_open_issues(
            repository,
            since=since.isoformat()
        )

        print(f"Found {len(issues)} issues\n")

        for issue in issues:

            print(
                f"#{issue['number']} "
                f"{issue['title']}"
            )

            print(issue["html_url"])
            print()


if __name__ == "__main__":
    main()