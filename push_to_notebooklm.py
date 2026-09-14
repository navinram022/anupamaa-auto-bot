# -*- coding: utf-8 -*-
"""
push_to_notebooklm.py
Standalone script to push any Anupamaa written update directly into NotebookLM:
Notebook: https://notebooklm.google.com/notebook/a611b8b8-35db-4b71-9b7e-034660c3874c
Uses the persistent Chrome profile so no re-login is required.
"""

import sys
import os
import logging
from config import PROFILE_DIR, NOTEBOOKLM_URL

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("NotebookLMSync")

def push_story_to_notebooklm(title: str, story_text: str) -> bool:
    try:
        from playwright.sync_api import sync_playwright
        from notebooklm_client import add_source_to_notebooklm
    except ImportError:
        logger.error("Playwright is not installed. Run: pip install playwright")
        return False

    logger.info("Connecting to Chrome Profile for NotebookLM...")
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
            logger.error(f"Failed to launch Chrome: {e}")
            print("\n[ERROR] Chrome profile is currently in use. Please close any open automated Chrome windows and try again.")
            return False

        page = browser_context.new_page()
        try:
            success = add_source_to_notebooklm(page, title, story_text)
            browser_context.close()
            return success
        except Exception as e:
            logger.error(f"NotebookLM push failed: {e}")
            browser_context.close()
            return False

if __name__ == "__main__":
    from story_scraper import fetch_latest_anupama_update
    print("1. Fetching latest Anupamaa Written Update...")
    data = fetch_latest_anupama_update()
    print(f"   Title: {data['title']}")
    print("2. Pushing to NotebookLM...")
    ok = push_story_to_notebooklm(data["title"], data["story"])
    if ok:
        print("[SUCCESS] Story successfully added to NotebookLM!")
    else:
        print("[FAILED] Could not add story to NotebookLM.")
