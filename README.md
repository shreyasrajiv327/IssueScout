# IssueScout

**IssueScout** is an open-source AI agent that helps developers discover GitHub issues that match their skills, interests, and previous contribution experience.

Instead of manually browsing hundreds of GitHub issues, IssueScout:

1. Fetches open issues from configured repositories.
2. Filters issues using the developer's skills and interests.
3. Uses an LLM to evaluate relevant issues.
4. Scores the developer–issue match.
5. Explains why an issue may be a good fit.
6. Can eventually notify the developer about strong matches.

The goal is to make GitHub contribution discovery more personalized and automated.

---

## Current Status

🚧 **Early prototype**

The current version successfully:

* Fetches open GitHub issues.
* Excludes pull requests from the issue list.
* Fetches a developer's previous pull requests.
* Performs a basic keyword-based relevance filter.
* Sends relevant issues to a local LLM through Ollama.
* Produces structured issue recommendations.
* Supports configurable repositories and developer profiles.

The project is intentionally still simple. There are several areas where the architecture and intelligence of the agent can be improved.

---

## How It Works

```text
                    GitHub
                       │
                       ▼
                Fetch open issues
                       │
                       ▼
              Relevance filtering
                       │
                       ▼
                 Relevant issues
                       │
                       ▼
                  LLM analysis
                       │
                       ▼
              Match score + reason
                       │
                       ▼
                 Recommendation
                       │
                       ▼
                  Notification
```

The long-term goal is:

```text
GitHub Issues
      │
      ▼
Cheap deterministic filtering
      │
      ▼
Candidate issues
      │
      ▼
AI-powered analysis
      │
      ├── Skill match
      ├── Previous experience
      ├── Interest match
      ├── Difficulty
      ├── Learning value
      └── Contribution likelihood
      │
      ▼
Ranked recommendations
      │
      ▼
Email notification
```

---

## Project Structure

```text
IssueScout/
├── agent/
│   ├── __init__.py
│   ├── github.py          # GitHub API client
│   ├── analyzer.py        # LLM-based issue analysis
│   ├── notifier.py        # Notification logic
│   └── scout.py           # Main agent workflow
│
├── config/
│   └── config.example.json
│
├── data/
│   └── state.json
│
├── .github/
│   └── workflows/
│       └── scout.yml
│
├── profile.json            # Local developer profile
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/shreyasrajiv327/IssueScout.git
cd IssueScout
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Configure GitHub authentication

Set a GitHub token as an environment variable:

```bash
export GITHUB_TOKEN="your_github_token"
```

The token is used by IssueScout to access the GitHub API.

---

## Configure Repositories

Copy the example configuration and modify it for the repositories you want to monitor.

```bash
cp config/config.example.json config/config.json
```

Example:

```json
{
  "repositories": [
    "cilium/cilium",
    "kubernetes/kubernetes"
  ],
  "min_score": 70,
  "lookback_hours": 24,
  "llm": {
    "provider": "ollama",
    "model": "qwen3:4b",
    "base_url": "http://localhost:11434/v1"
  }
}
```

Do not commit personal configuration or API credentials.

---

## Configure Your Developer Profile

The agent uses a developer profile containing:

* Programming languages
* Technical skills
* Areas of interest
* Learning goals
* Previous contributions

Example:

```json
{
  "name": "Developer",
  "github_username": "github_username",

  "skills": [
    "Go",
    "Python",
    "Kubernetes",
    "Linux"
  ],

  "areas_of_interest": [
    "Networking",
    "Cloud Infrastructure",
    "Security"
  ],

  "learning_goals": [
    "Learn more about distributed systems",
    "Improve Kubernetes knowledge"
  ],

  "previous_contributions": []
}
```

Your profile is used by the AI to determine whether an issue is relevant to you.

---

## Local LLM

The current prototype supports **Ollama** for local inference.

Install Ollama and pull the model you want to use:

```bash
ollama pull qwen3:4b
```

Start Ollama and verify that it is available:

```bash
curl http://localhost:11434/v1/models
```

The project uses the OpenAI-compatible API exposed by Ollama.

### Important

Local LLM inference can be resource-intensive, especially on machines with limited CPU/GPU resources.

The current prototype is **not optimized for inference performance yet**.

Future versions should support:

* Smaller/faster local models
* Better prompt efficiency
* Parallel inference where appropriate
* Cloud LLM providers
* Configurable inference strategies

---

## Running IssueScout

From the project root:

```bash
python3 agent/scout.py
```

Example output:

```text
Found 2 previous PRs

Repository: cilium/cilium
============================================================
Found 21 issues
Relevant issues after filtering: 19

Analyzing #48660: Cilium 1.20.x regression...
Score: 87/100
Recommendation: strongly_recommend
Reason: ...
Difficulty: medium
Learning value: high
URL: https://github.com/...
```

---

## Issue Scoring

The LLM currently evaluates issues using:

### Skill match

Does the issue involve technologies the developer already knows?

### Previous experience

Is the issue similar to work the developer has already done?

### Interest relevance

Does the issue align with the developer's interests?

### Difficulty

How difficult is the issue likely to be?

### Learning value

Would solving the issue help the developer develop useful skills?

### Contribution likelihood

Could the developer realistically make a useful contribution?

The model returns a score from `0–100`.

```text
90-100  Exceptional match
80-89   Strong match
70-79   Good match
50-69   Possible match
0-49    Poor match
```

Recommendations are:

```text
strongly_recommend
recommend
maybe
skip
```

---

## Known Limitations

This is an early prototype, and several parts are intentionally incomplete.

### 1. Relevance filtering is basic

The current pre-filter uses keyword matching against:

* Issue title
* Issue description
* Issue labels

This can produce false positives.

For example, a generic skill such as `Go` may match unrelated words.

A better approach would use weighted matching:

```text
Title match       → high weight
Label match       → high weight
Description match → lower weight
Exact technology  → higher score
Generic terms     → lower score
```

---

### 2. LLM inference can be slow

The current implementation sends issues to the LLM sequentially.

For a repository with many issues this can become expensive or slow, particularly when using a local model.

Potential improvements:

* Reduce the number of LLM candidates.
* Reduce prompt size.
* Cache developer context.
* Use smaller models.
* Parallelize inference carefully.
* Allow cloud LLM providers.
* Add configurable inference limits.

---

### 3. Issue state tracking is not complete

The current prototype uses a temporary lookback window when fetching issues.

A production implementation should persist information such as:

```text
issue number
repository
last analyzed timestamp
issue updated_at
previous score
previous recommendation
```

This would prevent the agent from repeatedly analyzing the same issues.

---

### 4. Previous contribution analysis can be improved

Currently, previous PRs are fetched from GitHub and provided to the analyzer.

A better implementation could build a structured developer contribution profile containing:

```text
Languages
Technologies
Subsystems
Types of changes
Files modified
Labels
Review history
Contribution frequency
```

This would allow much better matching between a developer and an issue.

---

### 5. Notifications are still being developed

The long-term goal is to notify developers about strong matches, rather than simply printing results to the terminal.

The preferred notification channel is email.

---

## Roadmap

### Phase 1 — Prototype

* [x] GitHub issue fetching
* [x] Pull request history fetching
* [x] Developer profile
* [x] Basic relevance filtering
* [x] LLM issue analysis
* [x] Structured scoring
* [ ] Email notifications

### Phase 2 — Better Matching

* [ ] Weighted relevance scoring
* [ ] Better technology extraction
* [ ] Improved previous-contribution analysis
* [ ] Issue deduplication
* [ ] State-based issue tracking
* [ ] Ranking of candidate issues

### Phase 3 — Agent Improvements

* [ ] Smaller/optimized prompts
* [ ] Parallel issue analysis
* [ ] LLM provider abstraction
* [ ] Local + cloud model support
* [ ] Retry/error handling
* [ ] Rate-limit handling

### Phase 4 — Automation

* [ ] GitHub Actions scheduled execution
* [ ] Email notifications
* [ ] Only notify above configurable score
* [ ] Avoid duplicate notifications
* [ ] Track previously recommended issues

### Phase 5 — Developer Experience

* [ ] Simple setup wizard
* [ ] Better configuration
* [ ] Contribution analytics
* [ ] Web dashboard
* [ ] Repository-specific customization

---

## Contributing

Contributions are welcome.

If you want to improve IssueScout, useful areas include:

### Matching

Improve how issues are matched to developer skills and experience.

### LLM efficiency

Reduce inference time and token usage while maintaining recommendation quality.

### GitHub intelligence

Improve extraction of information from:

* Issues
* Pull requests
* Labels
* Comments
* Repository structure
* Contribution history

### Notifications

Implement reliable email notifications and duplicate-alert prevention.

### Automation

Improve GitHub Actions execution, state management, and scheduled runs.

### Testing

Add unit and integration tests for the GitHub client, filtering, analyzer, and state management.

If you're making a larger change, opening an issue to discuss the approach first is encouraged.

---

## Design Philosophy

IssueScout is intended to be:

**Generic**

It should work with arbitrary GitHub repositories rather than being tied to a single project.

**Developer-centric**

Recommendations should consider the individual developer rather than simply ranking popular or easy issues.

**Conservative**

The agent should avoid pretending that a developer has experience they don't have.

**Resource-efficient**

Expensive LLM inference should only happen after cheap filtering has narrowed down the candidate set.

**Extensible**

The GitHub client, analyzer, notification system, and configuration should remain modular so they can evolve independently.

---

## License

See [LICENSE](LICENSE).
