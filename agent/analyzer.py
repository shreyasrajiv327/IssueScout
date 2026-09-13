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

        # Only send the information the model actually needs.
        developer_context = {
            "skills": profile.get("skills", []),
            "areas_of_interest": profile.get(
                "areas_of_interest", []
            ),
            "learning_goals": profile.get(
                "learning_goals", []
            )
        }

        # Only include useful information from previous PRs.
        contribution_context = []

        for pr in previous_prs[:10]:
            contribution_context.append({
                "title": pr.get("title", ""),
                "body": pr.get("body", "") or "",
                "labels": [
                    label.get("name", "")
                    for label in pr.get("labels", [])
                ]
            })

        labels = [
            label.get("name", "")
            for label in issue.get("labels", [])
        ]

        prompt = f"""
You are IssueScout.

Determine whether this GitHub issue is a good match
for the developer.

DEVELOPER:
{json.dumps(developer_context)}

PREVIOUS CONTRIBUTIONS:
{json.dumps(contribution_context)}

ISSUE:
Title: {issue.get("title", "")}
Labels: {json.dumps(labels)}
Description: {issue.get("body", "") or "No description"}

Evaluate:

- skill match
- previous experience match
- interest match
- difficulty
- learning value
- realistic contribution likelihood

Be conservative.
Do not invent experience or technical details.

Return ONLY valid JSON:

{{
  "score": 0,
  "recommendation": "skip",
  "reason": "",
  "difficulty": "medium",
  "learning_value": "medium",
  "relevant_experience": [],
  "likely_components": [],
  "suggested_first_steps": []
}}

Rules:

score:
90-100 exceptional match
80-89 strong match
70-79 good match
50-69 possible match
0-49 poor match

recommendation must be one of:
strongly_recommend
recommend
maybe
skip

difficulty must be one of:
easy
medium
hard

learning_value must be one of:
low
medium
high
"""

        response = self.client.chat.completions.create(
            model=self.model,
            extra_body={"think": False},
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=400
        )

        text = response.choices[0].message.content.strip()
 
        # Handle markdown JSON fences.
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0].strip()

        return json.loads(text)