import asyncio
import os
import json
from typing import List, Dict, Any, Optional
from .config import Config
from .github_client import GitHubClient
from .openai_client import OpenAIClient
from .diff_parser import parse_diff
from .comment_formatter import CommentFormatter

class Reviewer:
    def __init__(self, config: Config):
        self.config = config
        self.github = GitHubClient(config.github_token, config.github_repository)
        self.openai = OpenAIClient(config.openai_api_key, config.model)
        self.formatter = CommentFormatter()

    async def run_review(self, pr_number: int):
        # 1. Fetch metadata and diff
        pr_metadata = await self.github.get_pr_metadata(pr_number)
        diff_str = await self.github.get_pr_diff(pr_number)
        
        # 2. Parse diff
        file_diffs = parse_diff(diff_str)
        
        # 3. Filter files
        processed_files = []
        for fd in file_diffs:
            if any(pattern in fd.filename for pattern in self.config.exclude_patterns):
                continue
            if len(processed_files) >= self.config.max_files:
                break
            processed_files.append(fd)
            
        # 4. Run AI reviews in parallel
        tasks = [
            self.openai.review_file(fd, self.config.strictness, self.config.style_guide, self.config.review_focus)
            for fd in processed_files
        ]
        all_file_findings = await asyncio.gather(*tasks)
        
        # 5. Format comments for GitHub
        github_comments = []
        stats = {"info": 0, "warning": 0, "error": 0}
        
        # Severity priority mapping
        severity_rank = {"info": 0, "warning": 1, "error": 2}
        min_rank = severity_rank.get(self.config.min_severity, 1)

        for fd, findings in zip(processed_files, all_file_findings):
            for finding in findings:
                sev = finding.get("severity", "info").lower()
                if severity_rank.get(sev, 0) < min_rank:
                     continue
                
                stats[sev] = stats.get(sev, 0) + 1
                github_comments.append({
                    "path": fd.filename,
                    "line": finding.get("line"),
                    "side": "RIGHT",
                    "body": self.formatter.format_inline_comment(finding)
                })

        # 6. Generate summary review
        summary_body = await self.openai.generate_summary(all_file_findings, pr_metadata)
        
        # 7. Submit Review
        event = "COMMENT"
        if not github_comments and self.config.approve_if_clean:
            event = "APPROVE"
        elif any(f.get("severity") == "error" for file_findings in all_file_findings for f in file_findings):
            event = "REQUEST_CHANGES"

        await self.github.create_review(pr_number, github_comments, summary_body, event)
        print(f"✅ Review posted for PR #{pr_number}")
