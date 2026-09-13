import json
from datetime import datetime, timedelta, timezone

from github import GitHubClient
from analyzer import IssueAnalyzer


MAX_LLM_ISSUES = 10


def calculate_relevance(issue, profile):
    """
    Calculate a cheap relevance score before using the LLM.

    Title matches are weighted more heavily than
    description matches because titles are usually
    more representative of the actual issue.
    """

    title = issue.get("title", "").lower()
    body = (issue.get("body") or "").lower()

    labels = " ".join(
        label.get("name", "")
        for label in issue.get("labels", [])
    ).lower()

    skills = profile.get("skills", [])
    interests = profile.get("areas_of_interest", [])

    score = 0
    matched_keywords = []

    # Skills
    for skill in skills:
        keyword = skill.lower()

        if keyword in title:
            score += 5
            matched_keywords.append(skill)

        elif keyword in labels:
            score += 4
            matched_keywords.append(skill)

        elif keyword in body:
            score += 1
            matched_keywords.append(skill)

    # Areas of interest
    for interest in interests:
        keyword = interest.lower()

        if keyword in title:
            score += 5
            matched_keywords.append(interest)

        elif keyword in labels:
            score += 4
            matched_keywords.append(interest)

        elif keyword in body:
            score += 1
            matched_keywords.append(interest)

    return {
        "score": score,
        "matched_keywords": list(set(matched_keywords))
    }


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
    # Later this will be replaced
    # with persistent state tracking.

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
        # Calculate relevance
        # -------------------------

        ranked_issues = []

        for issue in issues:

            relevance = calculate_relevance(
                issue,
                profile
            )

            ranked_issues.append({
                "issue": issue,
                "relevance_score": relevance["score"],
                "matched_keywords": relevance[
                    "matched_keywords"
                ]
            })

        # Highest relevance first
        ranked_issues.sort(
            key=lambda item: item["relevance_score"],
            reverse=True
        )

        # -------------------------
        # Select candidates
        # -------------------------

        candidates = [
            item
            for item in ranked_issues
            if item["relevance_score"] > 0
        ]

        print(
            f"Relevant issues: {len(candidates)}"
        )

        if not candidates:
            print("No relevant issues found.")
            continue

        # Only send the best candidates
        # to the expensive LLM.
        candidates = candidates[:MAX_LLM_ISSUES]

        print(
            f"Sending top {len(candidates)} "
            f"issues to LLM"
        )

        print()

        # -------------------------
        # LLM analysis
        # -------------------------

        for candidate in candidates:

            issue = candidate["issue"]

            print(
                f"Analyzing #{issue['number']}: "
                f"{issue['title']}"
            )

            print(
                f"Local relevance score: "
                f"{candidate['relevance_score']}"
            )

            print(
                f"Matched: "
                f"{', '.join(candidate['matched_keywords'])}"
            )

            try:

                result = analyzer.analyze(
                    issue,
                    profile,
                    previous_prs
                )

                print(
                    f"AI Score: "
                    f"{result['score']}/100"
                )

                print(
                    f"Recommendation: "
                    f"{result['recommendation']}"
                )

                print(
                    f"Reason: "
                    f"{result['reason']}"
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
                    f"URL: "
                    f"{issue['html_url']}"
                )

            except Exception as e:

                print(
                    f"Failed to analyze "
                    f"#{issue['number']}: {e}"
                )

            print("-" * 60)


if __name__ == "__main__":
    main()

