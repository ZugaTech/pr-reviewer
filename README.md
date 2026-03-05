# AI-Powered PR Reviewer 🤖

A production-ready GitHub Action that automatically reviews pull requests using GPT-4o. It focuses on bugs, security, and performance while providing structured inline feedback and suggested fixes.

## Features

- **Structural Diff Analysis**: Parses unified diffs to provide context-aware feedback on exact line numbers.
- **Strictness Controls**: Choose from `low`, `medium`, `high`, or `paranoid` review modes.
- **Themed Focus**: Target specific areas like `security`, `performance`, or `style`.
- **Suggested Fixes**: Directly provides GitHub-formatted suggestion blocks for one-click application.
- **Smart Summary**: Posts a top-level summary review with a risk-level assessment.
- **Language Aware**: Automatically detects languages (Python, TS/JS, Go, Java, etc.) to apply relevant best practices.

## Usage

Add the following workflow to your repository in `.github/workflows/pr-reviewer.yml`:

```yaml
name: AI PR Reviewer
on:
 pull_request:
 types: [opened, synchronize]

jobs:
 review:
 runs-on: ubuntu-latest
 steps:
 - name: Checkout code
 uses: actions/checkout@v4

 - name: AI PR Reviewer
 uses: your-repo/pr-reviewer@main
 with:
 github_token: ${{ secrets.GITHUB_TOKEN }}
 openai_api_key: ${{ secrets.OPENAI_API_KEY }}
 model: "gpt-4o"
 strictness: "high"
 review_focus: "all"
```

## Inputs

| Name | Description | Default |
|------|-------------|---------|
| `github_token` | GitHub Token | Required |
| `openai_api_key` | OpenAI API Key | Required |
| `model` | OpenAI Model | `gpt-4o` |
| `strictness` | `low`, `medium`, `high`, `paranoid` | `medium` |
| `review_focus` | `all`, `bugs`, `security`, `performance`, `style` | `all` |
| `min_severity` | `info`, `warning`, `error` | `warning` |
| `approve_if_clean` | Approve PR if no issues found | `false` |

## Architecture

1. **Event Trigger**: Action activates on PR events.
2. **Context Gathering**: Fetches PR metadata and unified diff via GitHub REST API.
3. **Diff Parsing**: Structures diff into hunks and identifies modified lines.
4. **AI Review**: GPT-4o reviews each file in parallel using a specialized structured prompt.
5. **Formatting**: Findings are mapped to Markdown comments and suggested fixes.
6. **Delivery**: Batch review is submitted to GitHub.

## Security

- This action only has access to the metadata and diff of the pull request.
- The `openai_api_key` should be stored as a GitHub Secret.
- The action runs in a containerized environment.

## License

MIT