"""
Story Scraper for Anupamaa Written Updates from JustShowBiz.
Uses RSS feed for ultra-fast, 100% reliable extraction without Cloudflare blocking.
"""

import urllib.request
import re
import html
import logging
from config import JUSTSHOWBIZ_FEED_URL

logger = logging.getLogger("AnupamaaBot.Scraper")

def clean_story_html(raw_html: str) -> str:
    """Strip HTML tags, scripts, and promotional clutter from story content."""
    # Remove script and style tags
    clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    # Replace breaks and paragraphs with newlines
    clean = re.sub(r'<br\s*/?>', '\n', clean, flags=re.IGNORECASE)
    clean = re.sub(r'</p>', '\n\n', clean, flags=re.IGNORECASE)
    # Strip all remaining HTML tags
    clean = re.sub(r'<[^>]+>', '', clean)
    # Unescape HTML entities (&nbsp;, &#8217;, etc.)
    clean = html.unescape(clean)
    
    # Clean up excess whitespace and blank lines
    lines = []
    for line in clean.split('\n'):
        line = line.strip()
        # Filter out common ad / footer phrases
        if not line:
            continue
        if re.search(r'(also read|click to read|stay tuned to|justshowbiz|follow us on|advertisement)', line, re.IGNORECASE):
            # Skip promotional links
            if len(line) < 120 and ('read' in line.lower() or 'follow' in line.lower() or 'stay tuned' in line.lower()):
                continue
        lines.append(line)
        
    return '\n\n'.join(lines)

def fetch_latest_anupama_update() -> dict:
    """
    Fetches the latest Anupamaa Written Update article.
    Returns dict with keys: title, date, link, story.
    """
    logger.info("Fetching RSS feed from JustShowBiz...")
    req = urllib.request.Request(
        JUSTSHOWBIZ_FEED_URL,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
    )
    
    with urllib.request.urlopen(req, timeout=15) as response:
        feed_xml = response.read().decode('utf-8', errors='ignore')
        
    # Extract <item> blocks
    items = re.findall(r'<item>(.*?)</item>', feed_xml, re.DOTALL)
    if not items:
        raise ValueError("No items found in JustShowBiz RSS feed.")
        
    for item in items:
        title_m = re.search(r'<title>(.*?)</title>', item)
        title = html.unescape(title_m.group(1)) if title_m else ""
        
        # Check if this item is a Written Update
        if "written update" in title.lower() and "anupama" in title.lower():
            link_m = re.search(r'<link>(.*?)</link>', item)
            link = link_m.group(1).strip() if link_m else ""
            
            pub_date_m = re.search(r'<pubDate>(.*?)</pubDate>', item)
            pub_date = pub_date_m.group(1).strip() if pub_date_m else ""
            
            content_m = re.search(r'<content:encoded><!\[CDATA\[(.*?)\]\]></content:encoded>', item, re.DOTALL)
            if not content_m:
                content_m = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item, re.DOTALL)
                
            raw_content = content_m.group(1) if content_m else ""
            story_text = clean_story_html(raw_content)
            
            logger.info(f"Successfully found latest update: '{title}' ({len(story_text)} chars)")
            return {
                "title": title,
                "date": pub_date,
                "link": link,
                "story": story_text
            }
            
    raise ValueError("No Anupamaa Written Update found in the recent RSS items.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch_latest_anupama_update()
    print("--- TITLE ---")
    print(data["title"])
    print("\n--- LINK ---")
    print(data["link"])
    print(f"\n--- STORY LENGTH: {len(data['story'])} chars ---")
    print("\n--- FIRST 400 CHARS ---")
    print(data["story"][:400])
