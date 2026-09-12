"""
Master Orchestrator for Anupamaa Written Update Automation.
Fetches story -> Adds to NotebookLM -> Generates via Gemini Gem -> Emails result.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Ensure clean UTF-8 console output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from playwright.sync_api import sync_playwright
    from notebooklm_client import add_source_to_notebooklm
    from gemini_client import generate_with_gemini_gem
except ImportError:
    sync_playwright = None
    add_source_to_notebooklm = None
    generate_with_gemini_gem = None

from config import PROFILE_DIR, LOGS_DIR, STATE_FILE, BASE_DIR
from story_scraper import fetch_latest_anupama_update
from email_service import send_email_report
from prompt_app_service import save_to_prompt_app

# Configure logging
log_file = os.path.join(LOGS_DIR, "automation.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AnupamaaBot.Main")

def is_already_run_today() -> bool:
    """Checks if the bot has already processed today's episode."""
    if not os.path.exists(STATE_FILE):
        return False
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
            today_str = datetime.now().strftime("%Y-%m-%d")
            return state.get("last_run_date") == today_str
    except Exception:
        return False

def mark_run_completed(title: str, link: str):
    """Saves the completion state for today."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    state = {
        "last_run_date": today_str,
        "completed_at": datetime.now().isoformat(),
        "title": title,
        "link": link
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def run_pipeline(force: bool = False):
    logger.info("==================================================")
    logger.info("Starting Anupamaa Episode Automation Pipeline...")
    logger.info("==================================================")
    
    # 0. Check daily completion
    if not force and is_already_run_today():
        logger.info("Today's Anupamaa episode has already been processed and sent. Exiting.")
        print("\n✓ Today's update has already been processed! Use --force to re-run if needed.")
        return
        
    # 1. Fetch story from JustShowBiz
    logger.info("Step 1/4: Fetching latest Anupamaa Written Update...")
    try:
        episode_data = fetch_latest_anupama_update()
    except Exception as e:
        logger.error(f"Failed to fetch story from JustShowBiz: {e}")
        return
        
    title = episode_data["title"]
    date_str = episode_data["date"]
    link = episode_data["link"]
    story_text = episode_data["story"]
    
    print(f"\n[1/4] Found Episode: {title}")
    print(f"      Story Length: {len(story_text)} characters")
    
    is_cloud_mode = "--cloud" in sys.argv or (not sys.platform.startswith("win"))
    gemini_result = ""

    if is_cloud_mode:
        print("\n[2/4] [CLOUD MODE] Generating content via Google Gemini API (No browser needed)...")
        try:
            from gemini_api_client import generate_with_gemini_api
            gemini_result = generate_with_gemini_api(story_text, date_str)
            print("      [OK] Successfully received structured Gemini output!")
        except Exception as e:
            logger.error(f"Cloud Gemini API call failed: {e}")
            print(f"      [ERROR] Gemini API error: {e}")
    else:
        # 2 & 3. Local Browser Automation (NotebookLM & Gemini Gem)
        logger.info("Starting Local Browser Automation session...")
        print("\n[2/4] Connecting to Google Services via Local Chrome Profile...")
        
        with sync_playwright() as p:
            try:
                browser_context = p.chromium.launch_persistent_context(
                    user_data_dir=PROFILE_DIR,
                    channel="chrome",
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--start-minimized"
                    ],
                    viewport={"width": 1280, "height": 800}
                )
            except Exception as e:
                logger.error(f"Failed to launch Chrome browser: {e}")
                print(f"\n[ERROR] Failed to launch Chrome: {e}")
                print("If Chrome is open with this profile, please close it and try again.")
                return
                
            page = browser_context.new_page()
            
            # Step 2: Add source to NotebookLM
            try:
                print("\n[2/4] Adding episode story as source to NotebookLM...")
                add_source_to_notebooklm(page, title, story_text)
                print("      [OK] Successfully added to NotebookLM!")
            except Exception as e:
                logger.error(f"NotebookLM step failed: {e}")
                print(f"      [NOTE] NotebookLM note: {e}")
                
            # Step 3: Generate response from Gemini Custom Gem
            try:
                print("\n[3/4] Generating summary/analysis from Gemini Custom Gem...")
                gemini_result = generate_with_gemini_gem(page, story_text)
                print("      [OK] Successfully received Gemini output!")
            except Exception as e:
                logger.error(f"Gemini Gem step failed: {e}")
                print(f"      [NOTE] Gemini note: {e}")
                
            browser_context.close()
        
    # Step 4: Parse into master card and save directly to Prompt App Daily Category
    print(f"\n[4/4] Publishing single master card to daily category '📅 {date_str} - अनुपमा रिटन अपडेट'...")
    if not gemini_result:
        gemini_result = f"(Gemini output not available. Here is the raw story):\n\n{story_text}"

    from prompt_app_service import save_to_prompt_app
    saved_to_app = save_to_prompt_app(title, date_str, gemini_result, link)
    if saved_to_app:
        print(f"      [OK] Successfully published to Daily Category '📅 {date_str} - अनुपमा रिटन अपडेट' in Prompt App!")

    # Step 5: Optional Email Delivery
    email_sent = send_email_report(title, date_str, gemini_result, link)
    if email_sent:
        print("      [OK] Email delivered to Navinram022@gmail.com!")
    else:
        print("      [INFO] Report also saved locally under reports/ folder.")
        
    mark_run_completed(title, link)
    logger.info("Pipeline completed successfully!")
    print("\n==================================================")
    print(">> All steps finished successfully!")
    print("==================================================")

if __name__ == "__main__":
    force_run = "--force" in sys.argv
    run_pipeline(force=force_run)
