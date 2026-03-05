import json
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from .diff_parser import FileDiff

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def review_file(self, file_diff: FileDiff, strictness: str, style_guide: str, focus: str) -> List[Dict[str, Any]]:
        # Format the diff for the prompt
        diff_context = ""
        for hunk in file_diff.hunks:
            diff_context += f"@@ -{hunk.old_start},{hunk.old_count} +{hunk.new_start},{hunk.new_count} @@\n"
            for line in hunk.lines:
                prefix = "+" if line.type == "added" else "-" if line.type == "removed" else " "
                diff_context += f"{prefix}{line.content}\n"

        strictness_prompts = {
            "low": "Only flag critical bugs and security vulnerabilities. Be terse.",
            "medium": "Flag bugs, security issues, and significant performance problems. Suggest improvements where clearly beneficial.",
            "high": "Exhaustively review for bugs, security, performance, maintainability, and clarity. Flag anything that could cause issues.",
            "paranoid": "Review as if this code will run in a high-security financial system. Flag every potential issue including subtle logic errors, race conditions, injection risks, and any deviation from best practices."
        }

        system_prompt = f"""
You are an expert {file_diff.language} code reviewer. Your goal is to provide high-quality, actionable feedback on the provided diff.
{strictness_prompts.get(strictness, strictness_prompts['medium'])}

Focus areas: {focus}.
Style guide: {style_guide}.

Rules:
1. Provide feedback only on the lines that were ADDED or MODIFIED (marked with +).
2. For each issue, provide: a title, severity (info, warning, error), category, a detailed body, and a suggested code fix if possible.
3. Your output MUST be a JSON object with a 'comments' array.
4. Each comment must have 'line' (target line number in the NEW file) and 'side' (always "RIGHT").
5. Only suggest fixes that are syntactically correct and relevant.
"""

        user_prompt = f"File: {file_diff.filename}\n\nDiff:\n```diff\n{diff_context}\n```"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            data = json.loads(response.choices[0].message.content)
            return data.get("comments", [])
        except Exception as e:
            print(f"Error reviewing {file_diff.filename}: {e}")
            return []

    async def generate_summary(self, all_comments: List[Dict[str, Any]], pr_metadata: Dict[str, Any]) -> str:
        if not all_comments:
            return "✅ No significant issues found. Great job!"

        summary_prompt = f"""
Summarize the following code review comments for this PR.
PR Title: {pr_metadata.get('title')}
Author: {pr_metadata.get('user', {}).get('login')}

Provide an overall assessment, a risk level (low, medium, high), and a brief synthesis of the most important issues found.
Output format: Markdown. Use badges for risk levels.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior tech lead summarizing a code review."},
                    {"role": "user", "content": f"{summary_prompt}\n\nComments:\n{json.dumps(all_comments[:50])}"} # Truncate if too many
                ]
            )
            return response.choices[0].message.content
        except:
            return "Review completed with some findings. Please see inline comments."
