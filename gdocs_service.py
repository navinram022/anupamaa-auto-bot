# -*- coding: utf-8 -*-
"""
gdocs_service.py
Integrates with Google Apps Script Webhook to automatically generate
a fully styled and color-coded Master Google Doc for the day's Anupamaa content.

Webhook: https://script.google.com/macros/s/AKfycbx6HRy6G6OiTz7YMvgIQOmiJFENR70ez7Rcr_kMMPzfGmD4Sho4M6OSFLgUSRfyWZy6bA/exec
"""

import sys
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger("AnupamaaBot.GDocs")

GDOCS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbx6HRy6G6OiTz7YMvgIQOmiJFENR70ez7Rcr_kMMPzfGmD4Sho4M6OSFLgUSRfyWZy6bA/exec"


def format_master_gdoc_content(date_str: str, polls_text: str, video_script_text: str, cards: list) -> str:
    """
    Formats all content according to the master visual styling rules:
    - [FB POLL 1], [VIDEO 1], [REEL 2], [POST 1] headers
    - 'सीन: ' empty in orange
    - Crisp pure dark black text
    - No Markdown stars (**)
    """
    sections = []

    # Title Banner
    sections.append(f"================================================================================")
    sections.append(f"अनुपमा (ANUPAMAA) - संपूर्ण एपिसोड ड्राफ्ट व सोशल मीडिया मास्टर गाइड")
    sections.append(f"तारीख: {date_str}")
    sections.append(f"================================================================================\n")

    # भाग 1: 5 फेसबुक पोल पोस्ट्स
    sections.append(f"--------------------------------------------------------------------------------")
    sections.append(f"भाग 1 : 5 फेसबुक पोल पोस्ट्स (NO PHOTO / NO VIDEO - सीधी ऑडियंस वोटिंग)")
    sections.append(f"--------------------------------------------------------------------------------\n")
    sections.append(polls_text.strip())
    sections.append("\n\n")

    # भाग 2: वीडियो और रील्स
    sections.append(f"--------------------------------------------------------------------------------")
    sections.append(f"भाग 2 : वीडियो और रील्स स्क्रिप्ट्स (3 मिनट लॉन्ग वीडियो + 2 वर्टिकल रील्स)")
    sections.append(f"--------------------------------------------------------------------------------\n")
    sections.append(video_script_text.strip())
    sections.append("\n\n")

    # भाग 3: 12 फोटो पोस्ट्स
    sections.append(f"--------------------------------------------------------------------------------")
    sections.append(f"भाग 3 : 12 फोटो पोस्ट्स (1080×1350px - 4:5 रेशियो | फोटो टेक्स्ट + फेसबुक कैप्शन)")
    sections.append(f"--------------------------------------------------------------------------------\n")

    for card in cards:
        num = card.get("num", 0)
        if num == 0 or card.get("isNote", False):
            continue  # Skip note tiles for photo posts section

        title = card.get("title", f"Post {num}")
        photo_text = card.get("photoText", "").strip()
        caption = card.get("caption", "").strip()

        sections.append(f"[{title}]")
        sections.append(f"सीन: ")
        sections.append(f"फोटो पर लिखने वाला टेक्स्ट:")
        sections.append(photo_text)
        sections.append(f"\nफेसबुक कैप्शन:")
        sections.append(caption)
        sections.append(f"\n" + ("-" * 60) + "\n")

    return "\n".join(sections)


def send_to_google_docs(title: str, content: str, webhook_url: str = GDOCS_WEBHOOK_URL) -> str:
    """
    Sends the formatted text to the Google Apps Script Webhook.
    Returns the live Google Doc URL on success, or None on failure.
    """
    logger.info(f"Sending content ({len(content)} chars) to Google Docs: '{title}'...")
    payload = {
        "title": title,
        "content": content
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data_bytes,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("status") == "success":
                doc_url = res_data.get("url")
                logger.info(f"Google Doc created successfully! URL: {doc_url}")
                print(f"\n[SUCCESS] Master Google Doc created: {doc_url}")
                return doc_url
            else:
                err_msg = res_data.get("message", "Unknown error")
                logger.error(f"Google Apps Script error: {err_msg}")
                print(f"\n[ERROR] Google Apps Script error: {err_msg}")
                return None
    except Exception as e:
        logger.error(f"Failed to call Google Apps Script webhook: {e}")
        print(f"\n[ERROR] Failed to send to Google Docs: {e}")
        return None


if __name__ == "__main__":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("Testing Google Docs Webhook with test ping...")
    sample_content = (
        "अनुपमा टेस्ट ड्राफ्ट\n\n"
        "[FB POLL 1]\n"
        "मुद्दा: टेस्ट पोल सवाल\n"
        "विकल्प A: विकल्प 1\n"
        "विकल्प B: विकल्प 2\n"
    )
    url = send_to_google_docs("अनुपमा टेस्ट डॉक्यूमेंट", sample_content)
    print("Result URL:", url)
