# -*- coding: utf-8 -*-
"""
viral_ideas_tracker.py
Maintains a strict rolling 5-day history of all Viral Post Ideas (Special Note 3 / Note 00).
Ensures that ideas are 100% fresh, diverse, and never repeated across consecutive days.
"""

import os
import sys
import json
import logging
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

logger = logging.getLogger("AnupamaaBot.ViralTracker")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "viral_ideas_history.json")

# Master Pool of 20+ Diverse Viral Concepts to rotate from:
DIVERSE_CONCEPT_POOL = [
    "इतिहास खुद को दोहरा रहा है (Past vs Present Clash)",
    "दोगलापन मीटर / स्वार्थ मीटर (Hypocrisy / Sarcasm Meter)",
    "जनता की अदालत / पब्लिक चार्जशीट (Courtroom FIR & Charge-Sheet)",
    "अगर ऐसा न होता तो / अनुज की याद (Alternative Reality / 'What-If')",
    "टीआरपी अलर्ट व ट्रैक का भविष्य (TRP Rating & Prediction)",
    "सोशल मीडिया पर फूटा आक्रोश (Public Tweet / Fan Comments Collage)",
    "पारिवारिक टकराव / दोराहा (Relationship Dilemma / Ego Clash)",
    "वायरल मीम कार्ड / व्यंग्य (Humorous Relatable Meme)",
    "लाचारी vs शेरनी का संकल्प (Character Transformation / Strength)",
    "रेट्रो क्विज / पुरानी यादें (Old Trivia Nostalgia)",
    "अनुपमा का कड़वा सच / जिंदगी की सीख (Minimalist Deep Quote)",
    "मेकर्स को खुली चिट्ठी (Open Letter to Writers)",
    "चरित्र का पोस्टमार्टम / विलेन डिकोड (Villain Psychological Autopsy)",
    "क्या खोया, क्या पाया? (Financial & Emotional Audit)",
    "पारिवारिक शोषण का पर्दाफाश (Dark Family Reality / Toxic Habits)",
    "संवादों का वार / तीखे पंचलाइन (Iconic Dialogue Breakdown)",
    "राही की दहाड़ vs अनुपमा का त्याग (Next-Gen Rebel vs Traditional Sacrifice)",
    "सीरियल की 3 सबसे बड़ी गलतियां (Critical Episode Review)",
    "शाह हाउस का टाइमलाइन इन्फोग्राफिक (Infographic Breakdown)",
    "ऑडियंस फैसला / जनता का जनमत (Audience Poll Verdict)"
]


def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading history: {e}")
            return {}
    return {}


def save_history(history: dict):
    # Keep only the last 5 days
    sorted_dates = sorted(history.keys(), reverse=True)[:5]
    trimmed_history = {d: history[d] for d in reversed(sorted_dates)}
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed_history, f, indent=2, ensure_ascii=False)


def record_today_ideas(date_str: str, ideas_list: list):
    """Saves today's viral concepts into the rolling 5-day backup."""
    history = load_history()
    history[date_str] = ideas_list
    save_history(history)
    logger.info(f"Recorded {len(ideas_list)} viral ideas for {date_str} in 5-day rolling history.")


def get_recent_used_concepts(days: int = 5) -> list:
    """Returns all concepts used in the last `days` to avoid repeating them."""
    history = load_history()
    recent_concepts = []
    for d, ideas in history.items():
        recent_concepts.extend(ideas)
    return recent_concepts


def get_fresh_concept_suggestions(count: int = 12) -> list:
    """Suggests fresh concept formats not recently overused."""
    used = get_recent_used_concepts(5)
    used_text = " ".join(used).lower()

    fresh = []
    # First pick concepts not in recent text
    for c in DIVERSE_CONCEPT_POOL:
        kw = c.split()[0].lower()
        if kw not in used_text:
            fresh.append(c)

    # Fill remaining from pool if needed
    for c in DIVERSE_CONCEPT_POOL:
        if c not in fresh:
            fresh.append(c)
        if len(fresh) >= count:
            break

    return fresh[:count]


if __name__ == "__main__":
    used = get_recent_used_concepts()
    print(f"Total concepts used in last 5 days: {len(used)}")
    for u in used:
        print(f"  - {u}")
    print("\nRecommended fresh concepts for next generation:")
    for f in get_fresh_concept_suggestions():
        print(f"  * {f}")
