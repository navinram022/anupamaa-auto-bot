# -*- coding: utf-8 -*-
"""
create_12_cards.py (Super-Clean & Fast Viral Version)
- ZERO Stock Photo Layers (हटा दिया गया)
- ZERO Base Prompt Overwrites (मास्टर प्रॉम्प्ट्स 100% सुरक्षित)
- सिर्फ आज का Photo Text और Caption अपडेट करता है।
"""

import os
import sys
import re
import time
import json
import urllib.request
from datetime import datetime

# UTF-8 encoding support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Neetu Prompt Studio Firebase Settings
FIREBASE_PROJECT_ID = "neetu-prompts"
FIREBASE_API_KEY = "AIzaSyD5gZr4s10roOThEeQjleJ5Sq7_rO6bA8E"
FIRESTORE_CARDS_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/prompt_cards"

# 11 फिक्स्ड कार्ड्स की मास्टर मैपिंग (ये IDs कभी नहीं बदलेंगी)
FIXED_CARD_DEFINITIONS = {
    1: {"id": "card_1789034447674_sngz", "title": "Full Story", "order": 1.0},
    2: {"id": "card_1791304216988_smb6", "title": "Full Bullet Point", "order": 2.0},
    3: {"id": "card_1789034397369_5oed", "title": "Aage Kya Hoga", "order": 3.0},
    4: {"id": "card_1789032446590_pcgz", "title": "Lower Text / Sawaal", "order": 4.0},
    5: {"id": "card_1789624993427_6prb", "title": "Upper Text", "order": 5.0},
    6: {"id": "card_1789628648793_c9cz", "title": "Sandwich Poster", "order": 6.0},
    7: {"id": "card_1789032080591_d9zv", "title": "Speech Bubble", "order": 7.0},
    8: {"id": "card_1789032150782_qx9j", "title": "Single Speech", "order": 8.0},
    9: {"id": "card_1789624324875_gbgm", "title": "Middle Text", "order": 9.0},
    10: {"id": "card_1789032311726_sdwo", "title": "Morning Post", "order": 10.0},
    11: {"id": "card_1791087259200_p6gk", "title": "Kamar Tak", "order": 11.0}
}


def parse_posts_from_gemini(content: str) -> dict:
    """Gemini के आउटपुट से केवल Photo Text और Caption अलग करता है"""
    posts_data = {i: {"photo_text": "", "caption": ""} for i in range(1, 12)}
    if not content:
        return posts_data

    # Code fences और stars साफ़ करना
    cleaned = re.sub(r'```(?:text|plain)?\s*', '', content, flags=re.IGNORECASE)
    cleaned = re.sub(r'```', '', cleaned)
    cleaned = re.sub(r'\*{2,}', '', cleaned)

    # डिवाइडर्स द्वारा टुकड़ों में बाँटना
    chunks = re.split(r'(?:\r?\n)?\s*[-=]{5,}\s*(?:\r?\n)?', cleaned)
    current_post = None
    is_caption = False

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        first_line = chunk.splitlines()[0].strip()
        header_m = re.search(r'(?:(?:(\d+)[\.:\s]*)?\[?पोस्ट\s*(\d+)\]?|(?:Post\s*(\d+)))', first_line, re.IGNORECASE)
        if header_m:
            num_str = header_m.group(1) or header_m.group(2) or header_m.group(3)
            try:
                num = int(num_str)
                if 1 <= num <= 11:
                    current_post = num
                    is_caption = ('कैप्शन' in first_line.lower() or 'caption' in first_line.lower())
                    lines = chunk.splitlines()
                    body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                    if body:
                        if is_caption:
                            posts_data[num]['caption'] = body
                        else:
                            posts_data[num]['photo_text'] = body
            except Exception:
                pass
        elif current_post and 1 <= current_post <= 11:
            if is_caption:
                if posts_data[current_post]['caption']:
                    posts_data[current_post]['caption'] += '\n\n' + chunk
                else:
                    posts_data[current_post]['caption'] = chunk
            else:
                if posts_data[current_post]['photo_text']:
                    posts_data[current_post]['photo_text'] += '\n\n' + chunk
                else:
                    posts_data[current_post]['photo_text'] = chunk

    return posts_data


def update_12_cards_in_firestore(posts_data: dict) -> int:
    """
    सीधे Firestore में 11 कार्ड्स को अपडेट करता है:
    - सिर्फ Photo Text और Caption बदलता है
    - Base Prompt, फोटो और बाकी सेटिंग्स को 100% सुरक्षित रखता है
    """
    now_ms = str(int(time.time() * 1000))
    success_count = 0

    print("=" * 60)
    print("🚀 Updating 11 Cards in Firestore (Only PhotoText & Caption)...")
    print("=" * 60)

    for num in range(1, 12):
        card_def = FIXED_CARD_DEFINITIONS.get(num)
        if not card_def:
            continue

        card_id = card_def["id"]
        title = card_def["title"]
        p_info = posts_data.get(num, {})
        photo_text = p_info.get("photo_text", "").strip()
        caption = p_info.get("caption", "").strip()

        fields_to_update = {"updatedAt": {"integerValue": now_ms}}
        if photo_text:
            fields_to_update["photoText"] = {"stringValue": photo_text}
        if caption:
            fields_to_update["caption"] = {"stringValue": caption}

        payload = {"fields": fields_to_update}
        update_masks = ["updateMask.fieldPaths=" + k for k in fields_to_update.keys()]
        mask_query = "&".join(update_masks)

        url = f"{FIRESTORE_CARDS_URL}/{card_id}?key={FIREBASE_API_KEY}&{mask_query}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="PATCH"
        )

        try:
            with urllib.request.urlopen(req, timeout=15):
                print(f"✅ Card {num:>2}: '{title}' Updated!")
                success_count += 1
        except Exception as e:
            print(f"❌ Card {num:>2}: '{title}' Error: {e}")

    print(f"\n🎉 Finished: {success_count}/11 Cards successfully updated in-place!")
    return success_count


def update_top_card_in_firestore(title: str, story_text: str) -> bool:
    """Card 0: आज की पूरी लिखित कहानी को ऐप के टॉप नोट में सेव करता है"""
    now_ms = str(int(time.time() * 1000))
    card_id = "card_anupama_story_note"

    m = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)', str(title))
    top_title = f"Anupma {m.group(1)} {m.group(2)[:3].capitalize()}" if m else "Anupma Written Update"

    lead_lines = [l.strip() for l in story_text.splitlines() if l.strip()][:3]
    photo_text_preview = "\n".join(lead_lines)

    fields = {
        "title": {"stringValue": top_title},
        "category": {"stringValue": "📺 अनुपमा"},
        "order": {"doubleValue": -1.0},
        "isNote": {"booleanValue": True},
        "basePrompt": {"stringValue": story_text},
        "photoText": {"stringValue": photo_text_preview},
        "caption": {"stringValue": story_text},
        "updatedAt": {"integerValue": now_ms}
    }
    url = f"{FIRESTORE_CARDS_URL}/{card_id}?key={FIREBASE_API_KEY}"
    req = urllib.request.Request(
        url,
        data=json.dumps({"fields": fields}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    try:
        with urllib.request.urlopen(req, timeout=15):
            print(f"👑 Top Note: '{top_title}' Updated!")
            return True
    except Exception as e:
        print(f"❌ Top Note Error: {e}")
        return False


def save_offline_cards_package(title: str, clean_date: str, posts_data: dict, gemini_raw: str = "") -> str:
    """स्थानीय कंप्यूटर पर बैकअप सेव करता है"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(base_dir, "04_Daily_Episode_Backups")
    os.makedirs(backup_dir, exist_ok=True)

    tag_m = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)', clean_date)
    date_tag = f"{int(tag_m.group(1)):02d}{tag_m.group(2)[:3].lower()}" if tag_m else "today"

    txt_path = os.path.join(backup_dir, f"anupama_{date_tag}_offline_cards.txt")
    lines = [
        "=" * 80,
        f"📺 ANUPAMA DAILY MASTER PACKAGE : {clean_date}",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80
    ]

    for num in range(1, 12):
        p = posts_data.get(num, {})
        title_name = FIXED_CARD_DEFINITIONS.get(num, {}).get("title", f"पोस्ट {num}")
        lines.append("")
        lines.append(f"📌 [पोस्ट {num}] : {title_name}")
        lines.append("-" * 60)
        lines.append("📷 फोटो टेक्स्ट (Photo Text):")
        lines.append(p.get("photo_text", "(खाली)"))
        lines.append("")
        lines.append("📝 फेसबुक कैप्शन (Facebook Caption):")
        lines.append(p.get("caption", "(खाली)"))
        lines.append("-" * 60)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Backward compatibility file
    today_out = os.path.join(base_dir, "today_gemini_output.txt")
    if gemini_raw:
        with open(today_out, "w", encoding="utf-8") as f:
            f.write(gemini_raw)

    print(f"💾 Local Backup Saved: {txt_path}")
    return txt_path


def publish_all_12_cards(title: str = None, story_text: str = None, date_str: str = None, offline_only: bool = False) -> bool:
    """मास्टर फंक्शन जो पूरे 11 कार्ड्स और टॉप नोट को प्रोसेस करता है"""
    from gemini_api_client import generate_with_gemini_api
    from story_scraper import fetch_latest_anupama_update

    if not title or not story_text:
        story_data = fetch_latest_anupama_update()
        title = story_data["title"]
        story_text = story_data["story"]

    m = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})', title or "")
    clean_date = f"{m.group(1)} {m.group(2)} {m.group(3)}" if m else datetime.now().strftime("%d %B %Y")

    # 1. Gemini से 11 वायरल पोस्ट्स जनरेट कराएं
    gemini_text = generate_with_gemini_api(story_text, clean_date)
    posts_data = parse_posts_from_gemini(gemini_text)

    # 2. बैकअप फ़ाइल सेव करें
    save_offline_cards_package(title, clean_date, posts_data, gemini_text)

    if offline_only:
        print("\n🔒 OFFLINE MODE: Card package created locally. Firestore not modified.")
        return True

    # 3. टॉप नोट अपडेट करें
    update_top_card_in_firestore(title, story_text)

    # 4. 11 कार्ड्स में सिर्फ photoText और caption अपडेट करें
    count = update_12_cards_in_firestore(posts_data)
    return count >= 8
