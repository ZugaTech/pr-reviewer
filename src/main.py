import os
import json
import asyncio
from .config import Config
from .reviewer import Reviewer

async def main():
    config = Config()
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return

    # Load PR number from GITHUB_EVENT_PATH
    if not os.path.exists(config.github_event_path):
        print(f"❌ Event path not found: {config.github_event_path}")
        return

    with open(config.github_event_path, "r") as f:
        event_data = json.load(f)
        
    pr_number = event_data.get("pull_request", {}).get("number")
    
    if not pr_number:
        print("❌ Could not find pull request number in event data.")
        return

    print(f"🚀 Starting review for PR #{pr_number} in {config.github_repository}...")
    
    reviewer = Reviewer(config)
    
    try:
        await reviewer.run_review(pr_number)
    except Exception as e:
        print(f"❌ Review failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
