import json
from datetime import datetime, timedelta, timezone

from github import GitHubClient
from analyzer import IssueAnalyzer


def is_relevant(issue, profile):
    """
    Cheap pre-filter to avoid sending obviously
    irrelevant issues to the LLM.
    """

    text = (
        issue.get("title", "") + " " +
        issue.get("body", "")
    ).lower()

    # Include labels because they often contain useful
    # technical/category information.
    labels = " ".join(
        label.get("name", "")
        for label in issue.get("labels", [])
    ).lower()

    text = text + " " + labels

    keywords = (
        profile.get("skills", []) +
        profile.get("areas_of_interest", [])
    )

    return any(
        keyword.lower() in text
        for keyword in keywords
    )


def main():

    # -------------------------
    # Load configuration
    # -------------------------

    with open("config/config.example.json") as f:
        config = json.load(f)

    with open("profile.json") as f:
        profile = json.load(f)

    # -------------------------
    # Initialize clients
    # -------------------------

    github = GitHubClient()

    analyzer = IssueAnalyzer(
        config["llm"]
    )

    # -------------------------
    # Lookback window
    # -------------------------

    # Temporary for testing.
    # Later we will replace this with
    # persistent state tracking.

    since = (
        datetime.now(timezone.utc)
        - timedelta(days=30)
    )

    # -------------------------
    # Get previous contributions
    # -------------------------

    previous_prs = []

    for repository in config["repositories"]:

        prs = github.get_user_pull_requests(
            profile["github_username"],
            repository
        )

        previous_prs.extend(prs)

    print(
        f"Found {len(previous_prs)} previous PRs"
    )

    # -------------------------
    # Process repositories
    # -------------------------

    for repository in config["repositories"]:

        print()
        print(f"Repository: {repository}")
        print("=" * 60)

        # -------------------------
        # Fetch issues
        # -------------------------

        issues = github.get_open_issues(
            repository,
            since=since.isoformat()
        )

        print(
            f"Found {len(issues)} issues"
        )

        # -------------------------
        # Cheap relevance filter
        # -------------------------

        relevant_issues = [
            issue
            for issue in issues
            if is_relevant(issue, profile)
        ]

        print(
            f"Relevant issues after filtering: "
            f"{len(relevant_issues)}"
        )

        if not relevant_issues:
            print("No relevant issues found.")
            continue

        print()

        # -------------------------
        # LLM analysis
        # -------------------------

        for issue in relevant_issues:

            print(
                f"Analyzing #{issue['number']}: "
                f"{issue['title']}"
            )

            try:

                result = analyzer.analyze(
                    issue,
                    profile,
                    previous_prs
                )

                print(
                    f"Score: {result['score']}/100"
                )

                print(
                    f"Recommendation: "
                    f"{result['recommendation']}"
                )

                print(
                    f"Reason: {result['reason']}"
                )

                print(
                    f"Difficulty: "
                    f"{result['difficulty']}"
                )

                print(
                    f"Learning value: "
                    f"{result['learning_value']}"
                )

                print(
                    f"URL: {issue['html_url']}"
                )

            except Exception as e:

                print(
                    f"Failed to analyze "
                    f"#{issue['number']}: {e}"
                )

            print("-" * 60)


if __name__ == "__main__":
    main()