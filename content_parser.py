"""
content_parser.py
Intelligently parses Gemini Custom Gem output into:
1. A master structured card format with beautiful ASCII divider boxes separating
   Photo Text and Facebook Copy-Ready Captions for Posts 1 to 4, Polls, and Analysis.
2. Structured Notebook notes.
"""

import re
import time
from datetime import datetime

def clean_block(text: str) -> str:
    """Removes artifacts and redundant header lines inside a sub-block."""
    text = re.sub(r'Plaintext\s*', '', text, flags=re.IGNORECASE)
    lines = text.strip().split('\n')
    filtered = []
    for l in lines:
        l_str = l.strip()
        if re.match(r'^\[पोस्ट\s*\d+\].*', l_str):
            continue
        if re.match(r'^(फोटो में लिखने के लिए टेक्स्ट|फेसबुक कैप्शन)$', l_str):
            continue
        filtered.append(l)
    return '\n'.join(filtered).strip()

def format_full_master_card(gemini_text: str, episode_date: str = "") -> str:
    """
    Constructs a single, impeccably decorated master prompt card content with
    crystal-clear divider boxes separating Photo Text from Facebook Captions.
    """
    if not episode_date:
        episode_date = datetime.now().strftime("%d %b %Y")

    # Split text into sections
    parts = re.split(r'(?=\[पोस्ट\s*\d+\]|चरण\s*2|Poll|2\s*Poll|पोल\s*1)', gemini_text)

    post1_photo, post1_cap = "", ""
    post2_photo, post2_cap = "", ""
    post3_photo, post3_cap = "", ""
    post4_photo, post4_cap = "", ""
    analysis_text = ""
    poll_texts = []

    for p in parts:
        p_strip = p.strip()
        if not p_strip:
            continue
        if re.search(r'\[पोस्ट\s*1\].*?फोटो', p_strip, re.DOTALL):
            post1_photo = p_strip
        elif re.search(r'\[पोस्ट\s*1\].*?कैप्शन', p_strip, re.DOTALL):
            post1_cap = p_strip
        elif re.search(r'\[पोस्ट\s*2\].*?फोटो', p_strip, re.DOTALL):
            post2_photo = p_strip
        elif re.search(r'\[पोस्ट\s*2\].*?कैप्शन', p_strip, re.DOTALL):
            post2_cap = p_strip
        elif re.search(r'\[पोस्ट\s*3\].*?फोटो', p_strip, re.DOTALL):
            post3_photo = p_strip
        elif re.search(r'\[पोस्ट\s*3\].*?कैप्शन', p_strip, re.DOTALL):
            post3_cap = p_strip
        elif re.search(r'\[पोस्ट\s*4\].*?फोटो', p_strip, re.DOTALL):
            post4_photo = p_strip
        elif re.search(r'\[पोस्ट\s*4\].*?कैप्शन', p_strip, re.DOTALL):
            post4_cap = p_strip
        elif re.search(r'चरण\s*2', p_strip):
            analysis_text = p_strip
        elif re.search(r'(?:Poll|पोल)', p_strip, re.IGNORECASE):
            poll_texts.append(p_strip)

    header_banner = f"""╔══════════════════════════════════════════════════════════════════╗
║     📅 {episode_date} — अनुपमा संपूर्ण एपिसोड अपडेट        ║
╚══════════════════════════════════════════════════════════════════╝"""

    sections_output = [header_banner]

    def make_section(title, photo_raw, cap_raw):
        photo_clean = clean_block(photo_raw)
        cap_clean = clean_block(cap_raw)
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌── 📸 [फोटो पर लिखने वाला टेक्स्ट] ────────────────────────────────
{photo_clean}
└──────────────────────────────────────────────────────────────────

┌── 📋 [फेसबुक कैप्शन - इसे कॉपी करें] ─────────────────────────────
{cap_clean}
└──────────────────────────────────────────────────────────────────
"""

    if post1_photo or post1_cap:
        sections_output.append(make_section("[पोस्ट 1] : फुल स्टोरी पोस्टर", post1_photo, post1_cap))

    if post2_photo or post2_cap:
        sections_output.append(make_section("[पोस्ट 2] : 5 बुलेट्स पोस्टर", post2_photo, post2_cap))

    if post3_photo or post3_cap:
        sections_output.append(make_section("[पोस्ट 3] : 5 अपकमिंग ट्विस्ट्स पोस्टर", post3_photo, post3_cap))

    if post4_photo or post4_cap:
        sections_output.append(make_section("[पोस्ट 4] : एपिसोड की सबसे बड़ी घटना", post4_photo, post4_cap))

    if poll_texts:
        clean_polls = "\n\n".join(clean_block(pt) for pt in poll_texts)
        sections_output.append(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 [पोल पोस्ट्स] : ऑडियंस एंगेजमेंट व वोटिंग
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌── 🗳️ [फेसबुक पोल सवाल व विकल्प] ────────────────────────────────
{clean_polls}
└──────────────────────────────────────────────────────────────────
""")

    if analysis_text:
        clean_analysis = clean_block(analysis_text)
        sections_output.append(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 [गहरा विश्लेषण] : स्टोरी ट्रैक्स, वायरल आइडिया व अतिरिक्त संदर्भ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌── 💡 [एपिसोड विश्लेषण व सोशल मीडिया एंगल] ────────────────────────
{clean_analysis}
└──────────────────────────────────────────────────────────────────
""")

    # Fallback if split found nothing
    if len(sections_output) == 1:
        sections_output.append(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 अनुपमा संपूर्ण अपडेट
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{clean_block(gemini_text)}
""")

    return "\n".join(sections_output).strip()


def parse_gemini_output(gemini_text: str, episode_date: str = "") -> list:
    """Parses Gemini output into individual note objects for notebook storage."""
    if not episode_date:
        episode_date = datetime.now().strftime("%d %b %Y")

    notes = []
    now_ms = int(time.time() * 1000)

    post1_match = re.search(r'(\[पोस्ट 1\].*?)(?=\[पोस्ट 2\]|\Z)', gemini_text, re.DOTALL)
    post2_match = re.search(r'(\[पोस्ट 2\].*?)(?=\[पोस्ट 3\]|\Z)', gemini_text, re.DOTALL)
    post3_match = re.search(r'(\[पोस्ट 3\].*?)(?=\[पोस्ट 4\]|\Z)', gemini_text, re.DOTALL)
    post4_match = re.search(r'(\[पोस्ट 4\].*?)(?=चरण\s*2|Poll|पोल|\Z)', gemini_text, re.DOTALL)

    poll_match = re.search(r'((?:2\s*Poll|Poll|पोल).*?)(?=चरण\s*2|\Z)', gemini_text, re.DOTALL | re.IGNORECASE)
    if not poll_match:
        poll_match = re.search(r'(पोल\s*1:.*?)(?=चरण\s*2|\Z)', gemini_text, re.DOTALL | re.IGNORECASE)

    analysis_match = re.search(r'(चरण\s*2\s*:.*?)(?=(?:2\s*Poll|Poll|पोल)|\Z)', gemini_text, re.DOTALL | re.IGNORECASE)
    if not analysis_match:
        analysis_match = re.search(r'(चरण\s*2.*?)(?=\Z)', gemini_text, re.DOTALL | re.IGNORECASE)

    def add_note(suffix_id, title, content_text):
        if not content_text or len(content_text.strip()) < 20:
            return
        notes.append({
            "id": f"note_anupamaa_{datetime.now().strftime('%Y%m%d')}_{suffix_id}",
            "title": title,
            "content": clean_block(content_text),
            "createdAt": now_ms,
            "updatedAt": now_ms
        })

    if post1_match:
        add_note("post1", f"📌 [पोस्ट 1] फुल स्टोरी पोस्टर ({episode_date})", post1_match.group(1))
    if post2_match:
        add_note("post2", f"📌 [पोस्ट 2] 5 बुलेट्स पोस्टर ({episode_date})", post2_match.group(1))
    if post3_match:
        add_note("post3", f"📌 [पोस्ट 3] 5 अपकमिंग ट्विस्ट्स ({episode_date})", post3_match.group(1))
    if post4_match:
        add_note("post4", f"📌 [पोस्ट 4] सबसे बड़ी घटना ({episode_date})", post4_match.group(1))
    if poll_match:
        add_note("poll", f"📊 [पोल पोस्ट्स] ऑडियंस वोटिंग सवाल ({episode_date})", poll_match.group(1))
    if analysis_match:
        add_note("analysis", f"🔍 [गहरा विश्लेषण] स्टोरी ट्रैक्स ({episode_date})", analysis_match.group(1))

    if not notes:
        add_note("full", f"📺 अनुपमा संपूर्ण अपडेट ({episode_date})", gemini_text)

    return notes


def parse_individual_post_cards(gemini_text: str, episode_date: str = "") -> list:
    """
    Parses Gemini output into individual note cards for the daily category grid.
    Each item represents one Note Tile (Note 1, Note 2, etc.) in the Prompt App.
    """
    if not episode_date:
        episode_date = datetime.now().strftime("%d %b %Y")

    cards = []
    today_tag = datetime.now().strftime("%Y%m%d")
    now_ms = int(time.time() * 1000)
    category_name = f"📅 {episode_date} - अनुपमा रिटन अपडेट"

    # Split text into sections
    parts = re.split(r'(?=\[पोस्ट\s*\d+\]|चरण\s*2|Poll|2\s*Poll|पोल\s*1)', gemini_text)

    post_pairs = {}
    analysis_text = ""
    poll_texts = []

    for p in parts:
        p_strip = p.strip()
        if not p_strip:
            continue
        m_post = re.search(r'\[पोस्ट\s*(\d+)\]\s*:\s*(.*?)(?:\n|$)', p_strip)
        if m_post:
            p_num = int(m_post.group(1))
            p_title = m_post.group(2).strip()
            if p_num not in post_pairs:
                post_pairs[p_num] = {"title": p_title, "photo": "", "caption": ""}
            if "फोटो" in p_strip[:80]:
                post_pairs[p_num]["photo"] = p_strip
            elif "कैप्शन" in p_strip[:80]:
                post_pairs[p_num]["caption"] = p_strip
        elif re.search(r'चरण\s*2', p_strip):
            analysis_text = p_strip
        elif re.search(r'(?:Poll|पोल)', p_strip, re.IGNORECASE):
            poll_texts.append(p_strip)

    order_idx = 1

    # Add each post as a note card
    for p_num in sorted(post_pairs.keys()):
        p_data = post_pairs[p_num]
        title = f"[पोस्ट {p_num}] {p_data['title']}"
        photo_clean = clean_block(p_data["photo"])
        cap_clean = clean_block(p_data["caption"])

        decorated = f"""┌── 📸 [फोटो पर लिखने वाला टेक्स्ट] ────────────────────────────────
{photo_clean}
└──────────────────────────────────────────────────────────────────

┌── 📋 [फेसबुक कैप्शन - इसे कॉपी करें] ─────────────────────────────
{cap_clean}
└──────────────────────────────────────────────────────────────────"""

        cards.append({
            "id": f"card_anupamaa_{today_tag}_post_{p_num}",
            "title": title,
            "category": category_name,
            "basePrompt": decorated,
            "photoText": photo_clean[:120] if photo_clean else title,
            "caption": cap_clean if cap_clean else decorated,
            "order": order_idx,
            "isNote": True,
            "createdAt": now_ms,
            "updatedAt": now_ms
        })
        order_idx += 1

    # Polls note card
    if poll_texts:
        clean_polls = "\n\n".join(clean_block(pt) for pt in poll_texts)
        poll_decorated = f"""┌── 🗳️ [फेसबुक पोल सवाल व विकल्प] ────────────────────────────────
{clean_polls}
└──────────────────────────────────────────────────────────────────"""
        cards.append({
            "id": f"card_anupamaa_{today_tag}_polls",
            "title": "[पोल पोस्ट्स] ऑडियंस वोटिंग सवाल",
            "category": category_name,
            "basePrompt": poll_decorated,
            "photoText": "ऑडियंस पोल सवाल",
            "caption": clean_polls,
            "order": order_idx,
            "isNote": True,
            "createdAt": now_ms,
            "updatedAt": now_ms
        })
        order_idx += 1

    # Analysis note card
    if analysis_text:
        clean_analysis = clean_block(analysis_text)
        analysis_decorated = f"""┌── 💡 [एपिसोड विश्लेषण व सोशल मीडिया एंगल] ────────────────────────
{clean_analysis}
└──────────────────────────────────────────────────────────────────"""
        cards.append({
            "id": f"card_anupamaa_{today_tag}_analysis",
            "title": "[गहरा विश्लेषण] स्टोरी ट्रैक्स व वायरल आइडिया",
            "category": category_name,
            "basePrompt": analysis_decorated,
            "photoText": "एपिसोड विश्लेषण",
            "caption": clean_analysis,
            "order": order_idx,
            "isNote": True,
            "createdAt": now_ms,
            "updatedAt": now_ms
        })

    return cards


def extract_post_photo_texts(gemini_text: str) -> dict:
    """
    Extracts clean photo text for posts 1, 2, 3, and 4
    to directly populate the user's template cards.
    """
    parts = re.split(r'(?=\[पोस्ट\s*\d+\]|चरण\s*2|Poll|2\s*Poll|पोल\s*1)', gemini_text)
    photo_texts = {}

    for p in parts:
        p_strip = p.strip()
        if not p_strip:
            continue
        m_post = re.search(r'\[पोस्ट\s*(\d+)\]', p_strip)
        if m_post and "फोटो" in p_strip[:80]:
            p_num = int(m_post.group(1))
            photo_texts[p_num] = clean_block(p_strip)

    return photo_texts
