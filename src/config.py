import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class Config:
    github_token: str = field(default_factory=lambda: os.getenv("INPUT_GITHUB_TOKEN", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("INPUT_OPENAI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("INPUT_MODEL", "gpt-4o"))
    strictness: str = field(default_factory=lambda: os.getenv("INPUT_STRICTNESS", "medium"))
    style_guide: str = field(default_factory=lambda: os.getenv("INPUT_STYLE_GUIDE", "none"))
    review_focus: str = field(default_factory=lambda: os.getenv("INPUT_REVIEW_FOCUS", "all"))
    max_files: int = field(default_factory=lambda: int(os.getenv("INPUT_MAX_FILES", "25")))
    max_lines_per_file: int = field(default_factory=lambda: int(os.getenv("INPUT_MAX_LINES_PER_FILE", "500")))
    exclude_patterns: List[str] = field(default_factory=lambda: os.getenv("INPUT_EXCLUDE_PATTERNS", "*.md,*.txt,*.lock,*.sum,package-lock.json").split(","))
    post_summary: bool = field(default_factory=lambda: os.getenv("INPUT_POST_SUMMARY", "true").lower() == "true")
    min_severity: str = field(default_factory=lambda: os.getenv("INPUT_MIN_SEVERITY", "warning"))
    approve_if_clean: bool = field(default_factory=lambda: os.getenv("INPUT_APPROVE_IF_CLEAN", "false").lower() == "true")
    
    # GitHub Environment
    github_repository: str = field(default_factory=lambda: os.getenv("GITHUB_REPOSITORY", ""))
    github_event_path: str = field(default_factory=lambda: os.getenv("GITHUB_EVENT_PATH", ""))

    def validate(self):
        if not self.github_token:
            raise ValueError("github_token is required")
        if not self.openai_api_key:
            raise ValueError("openai_api_key is required")
        if not self.github_repository:
            raise ValueError("GITHUB_REPOSITORY env is missing")
