"""
prompt_app_service.py
Synchronizes Anupamaa Written Update directly into Prompt App:
1. Creates a dedicated Daily Category on the Home Screen:
   e.g. "📅 12 Sep 2026 - अनुपमा रिटन अपडेट"
2. Inside this category, places a single clean Note Box (no prompt card dabbe):
   - Clear title: "📅 [Date] - अनुपमा रिटन अपडेट"
   - Single clean Note Box with a direct Copy button
   - Clicking on the note box opens the entire decorated content with:
     - [पोस्ट 1] फुल स्टोरी पोस्टर
     - [पोस्ट 2] 5 बुलेट्स पोस्टर
     - [पोस्ट 3] 5 अपकमिंग ट्विस्ट्स
     - [पोस्ट 4] सबसे बड़ी घटना
     - [पोल पोस्ट्स] ऑडियंस वोटिंग सवाल
     - [गहरा विश्लेषण] स्टोरी ट्रैक्स व सोशल मीडिया एंगल
3. Completely dynamic: fits today's content seamlessly.
"""

import time
import json
import urllib.request
import urllib.error
import logging
from datetime import datetime
from content_parser import format_full_master_card, parse_gemini_output, parse_individual_post_cards, extract_post_photo_texts

logger = logging.getLogger("AnupamaaBot.PromptApp")

FIREBASE_PROJECT_ID = "neetu-prompts"
FIREBASE_API_KEY = "AIzaSyD5gZr4s10roOThEeQjleJ5Sq7_rO6bA8E"
FIRESTORE_CARDS_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/prompt_cards"
FIRESTORE_NOTES_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/app_meta/notes?key={FIREBASE_API_KEY}"


def save_individual_post_cards_to_firestore(cards: list) -> bool:
    """Saves each individual post note card into Firestore for the minimal tile grid."""
    success = True
    for card in cards:
        doc_id = card["id"]
        now_ms = str(card.get("createdAt", int(time.time() * 1000)))
        payload = {
            "fields": {
                "id": {"stringValue": doc_id},
                "title": {"stringValue": card["title"]},
                "category": {"stringValue": card["category"]},
                "basePrompt": {"stringValue": card["basePrompt"]},
                "photoText": {"stringValue": card.get("photoText", "")},
                "caption": {"stringValue": card.get("caption", "")},
                "order": {"integerValue": str(card.get("order", 0))},
                "isNote": {"booleanValue": True},
                "createdAt": {"integerValue": now_ms},
                "updatedAt": {"integerValue": now_ms},
                "layers": {"arrayValue": {"values": []}}
            }
        }
        url = f"{FIRESTORE_CARDS_URL}/{doc_id}?key={FIREBASE_API_KEY}"
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="PATCH"
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                logger.info(f"Published post tile '{card['title']}' to Firestore")
        except Exception as e:
            logger.error(f"Failed to publish card {doc_id}: {e}")
            success = False
    return success


def save_anupamaa_note_card(title: str, date_str: str, gemini_result: str) -> bool:
    """
    Saves a single clean Note Box into Firestore under the daily category.
    """
    today_tag = datetime.now().strftime("%Y%m%d")
    doc_id = f"card_anupamaa_{today_tag}"
    category_name = f"📅 {date_str} - अनुपमा रिटन अपडेट"
    card_title = f"📅 {date_str} - अनुपमा रिटन अपडेट"
    master_content = format_full_master_card(gemini_result, date_str)
    now_ms = str(int(time.time() * 1000))

    payload = {
        "fields": {
            "id": {"stringValue": doc_id},
            "title": {"stringValue": card_title},
            "category": {"stringValue": category_name},
            "basePrompt": {"stringValue": master_content},
            "photoText": {"stringValue": "अनुपमा आज का एपिसोड"},
            "caption": {"stringValue": master_content},
            "order": {"integerValue": "0"},
            "isNote": {"booleanValue": True},
            "createdAt": {"integerValue": now_ms},
            "updatedAt": {"integerValue": now_ms},
            "layers": {"arrayValue": {"values": []}}
        }
    }

    url = f"{FIRESTORE_CARDS_URL}/{doc_id}?key={FIREBASE_API_KEY}"
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            logger.info(f"Published Single Master Note '{card_title}' to Prompt App!")
            return True
    except Exception as e:
        logger.error(f"Failed to publish note card to Firestore: {e}")
        return False


def convert_note_to_firestore_map(note: dict) -> dict:
    """Converts a standard note dictionary to Firestore mapValue representation."""
    now_ms = str(int(time.time() * 1000))
    return {
        "mapValue": {
            "fields": {
                "id": {"stringValue": str(note.get("id", f"note_{now_ms}"))},
                "title": {"stringValue": str(note.get("title", "Untitled Note"))},
                "content": {"stringValue": str(note.get("content", ""))},
                "createdAt": {"integerValue": str(note.get("createdAt", now_ms))},
                "updatedAt": {"integerValue": str(note.get("updatedAt", now_ms))}
            }
        }
    }


def get_existing_cloud_notes() -> dict:
    """Fetches current notes document from Firestore to preserve user's personal notes."""
    try:
        req = urllib.request.Request(FIRESTORE_NOTES_URL)
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("fields", {})
    except Exception:
        return {}


def save_to_prompt_app_notes(title: str, date_str: str, parsed_notes: list) -> bool:
    """Saves structured notes to the app notebook."""
    if not parsed_notes:
        return False

    existing_fields = get_existing_cloud_notes()
    existing_notes_raw = []
    if "notes" in existing_fields:
        existing_notes_raw = existing_fields["notes"].get("arrayValue", {}).get("values", [])

    today_tag = datetime.now().strftime("%Y%m%d")
    preserved_notes = []
    for item in existing_notes_raw:
        item_id = item.get("mapValue", {}).get("fields", {}).get("id", {}).get("stringValue", "")
        if not (f"note_anupamaa_{today_tag}" in item_id):
            preserved_notes.append(item)

    new_firestore_notes = [convert_note_to_firestore_map(n) for n in parsed_notes]
    combined_notes = new_firestore_notes + preserved_notes
    first_active_id = parsed_notes[0]["id"]
    first_content = parsed_notes[0]["content"]
    now_ms = str(int(time.time() * 1000))
    trash_notes_val = existing_fields.get("trashNotes", {"arrayValue": {"values": []}})

    payload = {
        "fields": {
            "notes": {"arrayValue": {"values": combined_notes}},
            "activeNoteId": {"stringValue": first_active_id},
            "text": {"stringValue": first_content},
            "trashNotes": trash_notes_val,
            "updatedAt": {"integerValue": now_ms}
        }
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        FIRESTORE_NOTES_URL,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True
    except Exception:
        return False


# Template Card Mapping requested by User:
# Post 1 -> D Full Story
# Post 2 -> DT FULL POST
# Post 3 -> D AAGE KYA HOGA
# Post 4 -> DT Breaking News
TEMPLATE_CARD_MAPPINGS = {
    1: {
        "id": "card_1789032080591_d9zv",
        "name": "D Full Story",
        "desc": "[पोस्ट 1] फुल स्टोरी फोटो टेक्स्ट"
    },
    2: {
        "id": "card_1789032311726_sdwo",
        "name": "DT FULL POST",
        "desc": "[पोस्ट 2] 5 बुलेट पॉइंट्स फोटो टेक्स्ट"
    },
    3: {
        "id": "card_1789032150782_qx9j",
        "name": "D    AAGE   KYA   HOGA",
        "desc": "[पोस्ट 3] 5 अपकमिंग ट्विस्ट्स फोटो टेक्स्ट"
    },
    4: {
        "id": "card_1789032446590_pcgz",
        "name": "DT    Breaking    News",
        "desc": "[पोस्ट 4] बड़ी घटना फोटो टेक्स्ट"
    },
}


def update_user_template_cards(photo_texts: dict) -> bool:
    """
    Updates photoText in the user's pre-configured template cards:
    - Post 1 -> D Full Story
    - Post 2 -> DT FULL POST
    - Post 3 -> D AAGE KYA HOGA
    - Post 4 -> DT Breaking News
    Safely preserves all existing prompts, images, canvas layers, and styling.
    """
    now_ms = str(int(time.time() * 1000))
    all_ok = True

    for p_num, config in TEMPLATE_CARD_MAPPINGS.items():
        doc_id = config["id"]
        card_name = config["name"]
        text_to_set = photo_texts.get(p_num)

        if not text_to_set:
            logger.warning(f"No photo text extracted for Post {p_num}")
            continue

        payload = {
            "fields": {
                "photoText": {"stringValue": text_to_set},
                "updatedAt": {"integerValue": now_ms}
            }
        }

        url = f"{FIRESTORE_CARDS_URL}/{doc_id}?updateMask.fieldPaths=photoText&updateMask.fieldPaths=updatedAt&key={FIREBASE_API_KEY}"
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="PATCH"
        )

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                logger.info(f"✓ Successfully updated template card [{card_name}] with Post {p_num} photo text!")
        except Exception as e:
            logger.error(f"✗ Failed to update template card [{card_name}] ({doc_id}): {e}")
            all_ok = False

    return all_ok


def save_to_prompt_app(title: str, date_str: str, gemini_result: str, link: str = "") -> bool:
    """
    Main entry point:
    1. Publishes the individual minimal Note Tiles into the Daily Category on the Home Screen.
    2. Auto-populates the user's 4 template cards (D Full Story, DT FULL POST, D AAGE KYA HOGA, DT Breaking News).
    3. Syncs the modular notes into the Notebook.
    """
    # 1. Daily Category Note Tiles
    individual_cards = parse_individual_post_cards(gemini_result, date_str)
    cards_ok = save_individual_post_cards_to_firestore(individual_cards)

    # 2. Auto-populate 4 Template Cards (Daily Post)
    photo_texts = extract_post_photo_texts(gemini_result)
    template_ok = update_user_template_cards(photo_texts)

    # 3. Modular Notes
    notes = parse_gemini_output(gemini_result, date_str)
    notes_ok = save_to_prompt_app_notes(title, date_str, notes)

    return cards_ok and template_ok

