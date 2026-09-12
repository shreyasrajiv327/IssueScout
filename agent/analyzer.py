import json
from openai import OpenAI


class IssueAnalyzer:

    def __init__(self, llm_config):
        self.provider = llm_config["provider"]
        self.model = llm_config["model"]
        self.base_url = llm_config.get("base_url")

        if self.provider == "ollama":
            self.client = OpenAI(
                base_url=self.base_url,
                api_key="ollama"
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {self.provider}"
            )

    def analyze(self, issue, profile, previous_prs):

        prompt = f"""
You are IssueScout, an AI agent that helps
developers discover GitHub issues they are
well positioned to solve.

Analyze whether the developer should consider
working on this issue.

DEVELOPER PROFILE:
{json.dumps(profile, indent=2)}

PREVIOUS PULL REQUESTS:
{json.dumps(previous_prs, indent=2)}

GITHUB ISSUE:

Repository:
{issue.get("repository", "")}

Title:
{issue["title"]}

Number:
{issue["number"]}

URL:
{issue["html_url"]}

Labels:
{json.dumps(
    [label["name"] for label in issue.get("labels", [])],
    indent=2
)}

Description:
{issue.get("body") or "No description provided"}

Evaluate:

1. Skill match
2. Similarity to previous work
3. Relevance to the developer's interests
4. Difficulty
5. Learning value
6. Likelihood the developer could realistically contribute

Be conservative.

Do not invent technical details,
file paths, or previous experience.

Return ONLY valid JSON:

{{
    "score": 0,
    "recommendation": "strongly_recommend",
    "reason": "...",
    "difficulty": "medium",
    "learning_value": "high",
    "relevant_experience": [],
    "likely_components": [],
    "suggested_first_steps": []
}}

Score:

90-100 = exceptional match
80-89  = strong match
70-79  = good match
50-69  = possible match
0-49   = poor match

Recommendation must be one of:

"strongly_recommend"
"recommend"
"maybe"
"skip"
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        text = response.choices[0].message.content.strip()

        # Some models wrap JSON in markdown fences.
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0].strip()

        return json.loads(text)