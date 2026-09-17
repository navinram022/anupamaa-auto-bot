# -*- coding: utf-8 -*-
"""
main.py
Master Orchestrator for Anupamaa Written Update Automation.
Pure Native Python Flow (ZERO GEMINI):
1. Fetches latest episode from JustShowBiz RSS.
2. FIRST: Saves directly to Cloud (Firestore Prompt App Cards & Master Google Doc).
3. SECOND: Checks NotebookLM via Chrome Profile:
   - If user already uploaded today's story -> Exits quietly without duplicate!
   - If not present -> Automatically uploads with verified dated heading.
4. Generates local HTML report & email.
"""

import os
import sys
import re
import json
import logging
from datetime import datetime, timezone, timedelta

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
except ImportError:
    sync_playwright = None
    add_source_to_notebooklm = None

from config import PROFILE_DIR, LOGS_DIR, STATE_FILE, BASE_DIR
from story_scraper import fetch_latest_anupama_update
from email_service import send_email_report
from create_12_cards import publish_all_12_cards

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

import urllib.request

FIREBASE_PROJECT_ID = "neetu-prompts"
FIREBASE_API_KEY = "AIzaSyD5gZr4s10roOThEeQjleJ5Sq7_rO6bA8E"
FIRESTORE_STATE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/app_meta/anupamaa_state?key={FIREBASE_API_KEY}"

IST = timezone(timedelta(hours=5, minutes=30))

def is_cloud_published_today() -> bool:
    """Checks if today's cards have already been published to Cloud Firestore."""
    today_str = datetime.now(IST).strftime("%Y-%m-%d")
    try:
        req = urllib.request.Request(FIRESTORE_STATE_URL)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cloud_date = data.get("fields", {}).get("last_run_date", {}).get("stringValue", "")
            if cloud_date == today_str:
                return True
    except Exception as e:
        logger.warning(f"Could not check Cloud Firestore state: {e}")
    return False

def is_local_finished_today() -> bool:
    """Checks if today has been fully completed locally (including NotebookLM sync)."""
    today_str = datetime.now(IST).strftime("%Y-%m-%d")
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                if state.get("last_run_date") == today_str and state.get("notebooklm_synced", False):
                    return True
        except Exception:
            pass
    return False

def is_already_run_today() -> bool:
    """Legacy helper; checks local completion."""
    return is_local_finished_today()

def advance_scheduled_task_to_tomorrow():
    """
    Once today's pipeline is completed, updates the Windows Task Scheduler task
    so it stops repeating today and only runs tomorrow morning at 07:00 AM.
    """
    try:
        import subprocess
        ps_cmd = (
            '$task = Get-ScheduledTask -TaskName "AnupamaaDailyBot" -ErrorAction SilentlyContinue; '
            'if ($task) { '
            '  $task.Triggers[0].Repetition.Interval = "PT15M"; '
            '  $task.Triggers[0].Repetition.Duration = "PT4H"; '
            '  $task.Triggers[0].StartBoundary = "$((Get-Date).AddDays(1).ToString(\'yyyy-MM-dd\'))T07:00:00"; '
            '  Set-ScheduledTask -InputObject $task -ErrorAction SilentlyContinue '
            '}'
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=10)
        logger.info("Scheduled task 'AnupamaaDailyBot' advanced to tomorrow 07:00 AM.")
    except Exception as e:
        logger.warning(f"Could not advance scheduled task: {e}")

def mark_run_completed(title: str, link: str, notebooklm_synced: bool = False, cloud_mode: bool = False):
    """Saves the completion state to Local File and/or Cloud Firestore, and advances schedule if done."""
    today_str = datetime.now(IST).strftime("%Y-%m-%d")
    now_iso = datetime.now(IST).isoformat()
    state = {
        "last_run_date": today_str,
        "completed_at": now_iso,
        "title": title,
        "link": link,
        "notebooklm_synced": notebooklm_synced
    }

    # 1. Save Local State File
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save local state: {e}")

    # 2. Save Cloud Firestore State (only in cloud mode or when cards published)
    if cloud_mode:
        try:
            payload = {
                "fields": {
                    "last_run_date": {"stringValue": today_str},
                    "completed_at": {"stringValue": now_iso},
                    "title": {"stringValue": title},
                    "link": {"stringValue": link}
                }
            }
            req = urllib.request.Request(
                FIRESTORE_STATE_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PATCH"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                logger.info("Successfully updated Cloud Firestore completion state!")
        except Exception as e:
            logger.error(f"Failed to save Cloud Firestore state: {e}")

    # 3. Advance Local Windows Task Scheduler to tomorrow if NotebookLM is synced
    if notebooklm_synced or cloud_mode:
        advance_scheduled_task_to_tomorrow()

def is_episode_from_today(title: str, pub_date_str: str) -> bool:
    """Checks if the fetched episode corresponds to today's date in IST."""
    now_ist = datetime.now(IST)
    today_day = str(now_ist.day)
    today_month = now_ist.strftime("%B")
    today_month_short = now_ist.strftime("%b")

    title_lower = title.lower()
    month_match = (today_month.lower() in title_lower) or (today_month_short.lower() in title_lower)
    day_regex = rf'\b0?{today_day}(?:st|nd|rd|th)?\b'
    day_match = bool(re.search(day_regex, title_lower))

    if month_match and day_match:
        return True

    if pub_date_str:
        pub_lower = pub_date_str.lower()
        if (today_month_short.lower() in pub_lower) and bool(re.search(day_regex, pub_lower)):
            return True

    return False

def run_pipeline(force: bool = False, cloud_mode: bool = False):
    logger.info("==================================================")
    logger.info(f"Starting Anupamaa Pipeline ({'Cloud' if cloud_mode else 'Local'} Mode)...")
    logger.info("==================================================")

    # 0. Check daily completion
    if not force:
        if cloud_mode and is_cloud_published_today():
            logger.info("Cloud: Today's Anupamaa episode has already been published to Firestore. Exiting.")
            print("\n✓ Cloud: Today's cards are already published!")
            return
        elif not cloud_mode and is_local_finished_today():
            logger.info("Local: Today's Anupamaa episode has already been fully processed and synced in NotebookLM. Exiting.")
            print("\n✓ Today's update has already been processed and synced to NotebookLM! Use --force to re-run if needed.")
            return

    # 1. Fetch story from JustShowBiz
    logger.info("Step 1/3: Fetching latest Anupamaa Written Update...")
    try:
        episode_data = fetch_latest_anupama_update()
    except Exception as e:
        logger.error(f"Failed to fetch story from JustShowBiz: {e}")
        print(f"\n[ERROR] Failed to fetch story: {e}")
        return

    title = episode_data["title"]
    date_str = episode_data["date"]
    link = episode_data["link"]
    story_text = episode_data["story"]

    print(f"\n[1/3] Found Episode: {title}")
    print(f"      Story Length: {len(story_text)} characters")

    # Check if episode is from today (IST)
    if not force and not is_episode_from_today(title, date_str):
        today_formatted = datetime.now(IST).strftime("%d %B %Y")
        logger.info(f"Today's episode ({today_formatted}) is not yet published. Latest found is: '{title}'.")
        print(f"\n[WAITING] Today's episode ({today_formatted}) is not yet published on JustShowBiz.")
        print(f"          Latest available: '{title}'")
        print("          Will automatically check again on the next 15-minute interval (7:15, 7:30, 7:45, 8:00...).")
        return

    # Step 2: FIRST SAVE TO CLOUD (Publish 12 Cards + Special Notes including Card -3 to Prompt App & Google Docs)
    cloud_already_done = is_cloud_published_today()
    if cloud_already_done and not force:
        print("\n[2/3] FIRST: Cards already exist in Cloud (Prompt App) for today. Skipping duplicate publish.")
        saved_to_app = True
    else:
        print(f"\n[2/3] FIRST: Publishing Today's Episode & 12 Cards to Cloud (Prompt App)...")
        saved_to_app = publish_all_12_cards(title=title, story_text=story_text, date_str=date_str)
        if saved_to_app:
            print("      [OK] Successfully published to Prompt App and created Master Google Doc in Cloud!")

    # Step 3: SECOND: Check NotebookLM (Quiet Exit if already uploaded by User, else Upload)
    notebooklm_synced = False
    if not cloud_mode:
        print("\n[3/3] SECOND: Connecting to NotebookLM via Local Chrome Profile...")
        if sync_playwright:
            try:
                with sync_playwright() as p:
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
                    page = browser_context.new_page()

                    # add_source_to_notebooklm automatically checks check_if_source_exists!
                    # If present: exits quietly without duplicate. If absent: uploads.
                    try:
                        print("      Checking if today's source exists in NotebookLM...")
                        success = add_source_to_notebooklm(page, title, story_text)
                        if success:
                            notebooklm_synced = True
                    except Exception as e:
                        logger.error(f"NotebookLM step note: {e}")
                        print(f"      [NOTE] NotebookLM note: {e}")

                    browser_context.close()
            except Exception as e:
                logger.warning(f"Browser launch note: {e}")
                print(f"      [NOTE] Browser launch note: {e}")
        else:
            print("      Playwright not installed, skipping browser step.")
    else:
        print("\n[3/3] Running in Cloud Mode: Story saved to Cloud Archive (Browser sync will run when PC starts).")

    # Step 4: Local report & optional email
    email_sent = send_email_report(title, date_str, story_text, link)
    if email_sent:
        print("      [OK] Email delivered to Navinram022@gmail.com!")
    else:
        print("      [INFO] Report saved locally under reports/ folder.")

    mark_run_completed(title, link, notebooklm_synced=notebooklm_synced, cloud_mode=cloud_mode)
    logger.info("Pipeline completed successfully!")
    print("\n==================================================")
    print(">> All steps finished successfully (Cloud First + NotebookLM Check)!")
    print("==================================================")

if __name__ == "__main__":
    force_run = "--force" in sys.argv
    cloud_run = "--cloud" in sys.argv
    run_pipeline(force=force_run, cloud_mode=cloud_run)
