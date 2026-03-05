from typing import Dict, Any

class CommentFormatter:
    @staticmethod
    def format_inline_comment(comment: Dict[str, Any]) -> str:
        # Severity emojis
        severity_icons = {
            "info": "💡",
            "warning": "⚠️",
            "error": "❌"
        }
        icon = severity_icons.get(comment.get("severity", "info").lower(), "💡")
        
        title = comment.get("title", "Code Review Comment")
        body = comment.get("body", "")
        category = comment.get("category", "")
        suggested_fix = comment.get("suggested_fix")
        
        formatted_body = f"{icon} **[{category.upper()}] {title}**\n\n{body}\n"
        
        if suggested_fix:
            formatted_body += f"\n```suggestion\n{suggested_fix.strip()}\n```"
            
        return formatted_body

    @staticmethod
    def format_summary_review(overall_assessment: str, risk_level: str, stats: Dict[str, int]) -> str:
        risk_color = "red" if risk_level.lower() == "high" else "yellow" if risk_level.lower() == "medium" else "green"
        badge = f"![Risk: {risk_level}](https://img.shields.io/badge/Risk-{risk_level}-{risk_color})"
        
        lines = [
            f"# AI Code Review Summary {badge}\n",
            "## Stats",
            f"- ❌ Errors: {stats.get('error', 0)}",
            f"- ⚠️ Warnings: {stats.get('warning', 0)}",
            f"- 💡 Suggestions: {stats.get('info', 0)}\n",
            "## Overall Assessment",
            overall_assessment
        ]
        
        return "\n".join(lines)
