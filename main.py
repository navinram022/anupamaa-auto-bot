# -*- coding: utf-8 -*-
"""
main.py
Master Orchestrator for Anupamaa Written Update Automation.
Pure Streamlined Flow dedicated to Neetu Prompt Studio:
1. Fetches latest episode from JustShowBiz RSS.
2. Generates 11 High-Impact Viral Posts via Gemini AI.
3. Updates Top Note & 11 Prompt Studio Cards in Firestore (Only PhotoText & Caption).
4. Saves local backup and locks for today.
"""

import os
import sys
import re
import json
import logging
import urllib.request
from datetime import datetime, timezone, timedelta

# UTF-8 console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import LOGS_DIR, STATE_FILE, BASE_DIR
from story_scraper import fetch_latest_anupama_update
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


def advance_scheduled_task_to_tomorrow():
    """Advances Windows Task Scheduler to tomorrow morning 07:00 AM once done."""
    try:
        import subprocess
        ps_cmd = (
            '$task = Get-ScheduledTask -TaskName "AnupamaaDailyBot" -ErrorAction SilentlyContinue; '
            'if ($task) { '
            '  $task.Triggers[0].Repetition.Interval = "PT15M"; '
            '  $task.Triggers[0].Repetition.Duration = "PT4H30M"; '
            '  $task.Triggers[0].StartBoundary = "$((Get-Date).AddDays(1).ToString(\'yyyy-MM-dd\'))T07:00:00"; '
            '  Set-ScheduledTask -InputObject $task -ErrorAction SilentlyContinue '
            '}'
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=10)
        logger.info("Scheduled task 'AnupamaaDailyBot' advanced to tomorrow 07:00 AM.")
    except Exception as e:
        logger.warning(f"Could not advance scheduled task: {e}")


def mark_run_completed(title: str, link: str, cloud_mode: bool = False):
    """Saves completion state to Local File and Cloud Firestore."""
    today_str = datetime.now(IST).strftime("%Y-%m-%d")
    now_iso = datetime.now(IST).isoformat()
    state = {
        "last_run_date": today_str,
        "completed_at": now_iso,
        "title": title,
        "link": link
    }

    # 1. Save Local State File
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save local state: {e}")

    # 2. Save Cloud Firestore State
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
        with urllib.request.urlopen(req, timeout=10):
            logger.info("Successfully updated Cloud Firestore completion state!")
    except Exception as e:
        logger.error(f"Failed to save Cloud Firestore state: {e}")

    if not cloud_mode:
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


def run_pipeline(force: bool = False, cloud_mode: bool = False, offline_mode: bool = False):
    logger.info("==================================================")
    logger.info(f"Starting Anupamaa Pipeline ({'Offline Staging' if offline_mode else ('Cloud' if cloud_mode else 'Local')} Mode)...")
    logger.info("==================================================")

    # 0. Safety Lock check
    if not offline_mode and not force:
        if is_cloud_published_today():
            logger.info("Cloud: Today's cards are already published in Firestore! Safety lock active.")
            print("\n🛡️ [SAFETY LOCK ACTIVE]: Today's episode is already published in Neetu Prompt Studio!")
            print("   Bot will NOT run again today to keep your custom edits 100% safe.")
            return

    # 1. Fetch story from JustShowBiz
    logger.info("Step 1/2: Fetching latest Anupamaa Written Update...")
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

    print(f"\n[1/2] Found Episode: {title}")
    print(f"      Story Length: {len(story_text)} characters")

    # Check date
    if not force and not offline_mode and not is_episode_from_today(title, date_str):
        today_formatted = datetime.now(IST).strftime("%d %B %Y")
        logger.info(f"Today's episode ({today_formatted}) is not yet published on JustShowBiz. Latest found: '{title}'.")
        print(f"\n[WAITING] Today's episode ({today_formatted}) is not yet published on JustShowBiz.")
        print(f"          Latest available: '{title}'")
        return

    # 2. Cards Generation & Firestore Publish
    print(f"\n[2/2] Generating & Publishing 11 Viral Cards to Neetu Prompt Studio...")
    saved_to_app = publish_all_12_cards(title=title, story_text=story_text, date_str=date_str, offline_only=offline_mode)
    if saved_to_app:
        print("      [OK] Successfully published to Neetu Prompt Studio Firestore!")

    if not offline_mode:
        mark_run_completed(title, link, cloud_mode=cloud_mode)

    logger.info("Pipeline completed successfully! Locked for today.")
    print("\n==================================================")
    print(">> All steps finished successfully! Studio cards updated.")
    print("==================================================")


if __name__ == "__main__":
    force_run = "--force" in sys.argv
    cloud_run = "--cloud" in sys.argv
    offline_run = "--offline" in sys.argv
    run_pipeline(force=force_run, cloud_mode=cloud_run, offline_mode=offline_run)
