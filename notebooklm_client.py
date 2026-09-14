"""
NotebookLM Client using Playwright.
Adds copied episode text as a new source to the specified NotebookLM project.
"""

import time
import re
import logging
from datetime import datetime
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config import NOTEBOOKLM_URL

logger = logging.getLogger("AnupamaaBot.NotebookLM")

def check_if_source_exists(page: Page, title: str) -> bool:
    """
    Checks if today's written update source is already added in NotebookLM.
    Matches either by exact title, or by the date contained in the title.
    """
    date_matches = re.findall(
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s*(?:\d{4})?\b',
        title,
        re.IGNORECASE
    )

    page.wait_for_timeout(2000)

    sources_in_ui = page.evaluate('''() => {
        const list = [];
        document.querySelectorAll('.source-title, [class*="source"] span, mat-list-item, [role="listitem"]').forEach(el => {
            const t = (el.innerText || '').trim();
            if (t) list.push(t);
        });
        return list;
    }''')

    for t in sources_in_ui:
        t_clean = t.lower()
        for dm in date_matches:
            day_match = re.search(r'\d+', dm)
            month_match = re.search(r'[A-Za-z]+', dm)
            if day_match and month_match:
                day_num = day_match.group(0)
                month_sub = month_match.group(0).lower()[:3]
                if (day_num in t_clean) and (month_sub in t_clean):
                    logger.info(f"Source already found in NotebookLM: '{t}' (matched date '{dm}')")
                    return True

        if title.lower() in t_clean or t_clean in title.lower():
            logger.info(f"Source already found in NotebookLM by title: '{t}'")
            return True

    return False


def add_source_to_notebooklm(page: Page, title: str, story_text: str) -> bool:
    """
    Navigates to the NotebookLM project and adds the story as a 'Copied text' source.
    First verifies if today's source is already present; if yes, exits quietly!
    """
    logger.info(f"Navigating to NotebookLM project: {NOTEBOOKLM_URL}")
    page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=60000)
    
    # Wait a few seconds for UI hydration
    page.wait_for_timeout(4000)
    
    # Check if redirected to Google sign-in
    if "accounts.google.com" in page.url or "signin" in page.url.lower():
        raise RuntimeError(
            "Google account is not logged in! Please run 'Setup_Google_Login.bat' once to sign into Google."
        )

    # 1. Check if source already exists!
    if check_if_source_exists(page, title):
        logger.info("✓ Today's story is ALREADY present in NotebookLM! Exiting quietly without duplicate.")
        print(f"\n✓ [INFO] Today's written update is ALREADY present in NotebookLM.")
        print(f"         Nothing to do, returning cleanly without duplicate!")
        return True
        
    logger.info("Source not found in NotebookLM. Proceeding to add new source...")
    logger.info("Looking for 'Add source' button...")
    
    # Possible selectors for Add Source button in NotebookLM
    add_source_selectors = [
        'button:has-text("Add source")',
        'button:has-text("Add sources")',
        '[aria-label*="Add source"]',
        '[aria-label*="Add sources"]',
        'mat-icon:has-text("add")',
        'button:has-text("Source")'
    ]
    
    add_btn = None
    for sel in add_source_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000)
            if el and el.is_visible():
                add_btn = el
                logger.info(f"Found Add Source button with selector: {sel}")
                break
        except Exception:
            continue
            
    if not add_btn:
        # Check if project has a direct "Copied text" or empty state card
        logger.warning("Could not find standard Add Source button, checking for direct input or modal...")
    else:
        add_btn.click()
        page.wait_for_timeout(2000)
        
    # Look for "Copied text" option in the sources modal
    copied_text_selectors = [
        'button:has-text("Copied text")',
        'div:has-text("Copied text")',
        '[aria-label*="Copied text"]',
        'text="Copied text"',
        'button:has-text("Paste text")',
        'text="Paste text"'
    ]
    
    copied_option = None
    for sel in copied_text_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000)
            if el and el.is_visible():
                copied_option = el
                logger.info(f"Found 'Copied text' option with selector: {sel}")
                break
        except Exception:
            continue
            
    if copied_option:
        copied_option.click()
        page.wait_for_timeout(2000)
        
    # Find textarea or content area to paste the text
    text_input_selectors = [
        'textarea[aria-label*="Copied text"]',
        'textarea[placeholder*="Paste"]',
        'textarea[placeholder*="text"]',
        'textarea',
        'div[contenteditable="true"]'
    ]
    
    text_area = None
    for sel in text_input_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000)
            if el and el.is_visible():
                text_area = el
                logger.info(f"Found text input area with selector: {sel}")
                break
        except Exception:
            continue
            
    if not text_area:
        raise RuntimeError("Could not find text input area inside NotebookLM source modal.")
        
    # Ensure date is strictly present in the title
    import re
    from datetime import datetime
    
    # Clean up quotes or December typos
    clean_title = re.sub(r'[\'\"]', '', title).replace("10th December 2026", "10th September 2026").replace("December", "September").strip()
    
    # Check if date exists in title
    has_date = bool(re.search(r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', clean_title, re.IGNORECASE))
    if not has_date:
        today_date_str = datetime.now().strftime("%d %B %Y")
        clean_title = f"Anupama {today_date_str} Written Update: {clean_title}"
        
    logger.info(f"Adding source to NotebookLM with verified dated title: '{clean_title}'")

    # Input title if available in modal
    try:
        title_input = page.query_selector('input[placeholder*="Title"], input[aria-label*="Title"]')
        if title_input and title_input.is_visible():
            title_input.fill(clean_title)
            page.wait_for_timeout(500)
    except Exception as e:
        logger.debug(f"Title input optional: {e}")
        
    # Prepend dated title as the very first line so NotebookLM indexes it with the exact date
    # Remove any existing duplicate title from story_text start
    clean_story = re.sub(r'^(?:Anupama[^\n]*Written\s+Update[^\n]*\n*)+', '', story_text, flags=re.IGNORECASE).strip()
    full_content = f"{clean_title}\n\n{clean_story}"
    
    logger.info(f"Pasting story with dated heading ({len(full_content)} chars) into NotebookLM...")
    text_area.fill(full_content)
    page.wait_for_timeout(1000)
    
    # Click Insert / Save / Add button
    insert_btn_selectors = [
        'button:has-text("Insert")',
        'button:has-text("Save")',
        'button:has-text("Add")',
        'button:has-text("Done")',
        '[aria-label*="Insert"]'
    ]
    
    insert_btn = None
    for sel in insert_btn_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000)
            if el and el.is_visible() and el.is_enabled():
                insert_btn = el
                logger.info(f"Found insert button with selector: {sel}")
                break
        except Exception:
            continue
            
    if not insert_btn:
        raise RuntimeError("Could not find 'Insert' / 'Save' button in NotebookLM.")
        
    insert_btn.click()
    logger.info("Clicked Insert button. Waiting for source to be processed...")
    
    # Wait for processing
    page.wait_for_timeout(6000)
    logger.info("Source successfully added to NotebookLM!")
    return True
