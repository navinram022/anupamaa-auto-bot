# -*- coding: utf-8 -*-
"""
generate_dynamic_cards.py
Dynamically creates and publishes the complete 12 Photo Post Cards + Special Notes
into Firestore for Prompt App for ANY given date and story.
"""

import os
import sys
import re
import time
import json
import socket
import urllib.request
import urllib.error
from datetime import datetime

# Force UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Force IPv4 resolution
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(*args, **kwargs):
    results = _orig_getaddrinfo(*args, **kwargs)
    ipv4 = [r for r in results if r[0] == socket.AF_INET]
    return ipv4 if ipv4 else results
socket.getaddrinfo = _ipv4_getaddrinfo

FIREBASE_PROJECT_ID = "neetu-prompts"
FIREBASE_API_KEY = "AIzaSyD5gZr4s10roOThEeQjleJ5Sq7_rO6bA8E"
FIRESTORE_CARDS_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/prompt_cards"
FIRESTORE_NOTES_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/app_meta/notes?key={FIREBASE_API_KEY}"

CARD_PROMPT_TEMPLATES = {
    1: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), फिल्मी पोस्टर स्टाइल।

चेहरा व एक्सप्रेशन 100% लॉक:
- दी गई तस्वीरों का असली चेहरा और ओरिजिनल फेशियल एक्सप्रेशन 100% लॉक रखें।
- AI कलाकार के चेहरे, फेशियल स्ट्रक्चर या एक्सप्रेशन में कोई भी बदलाव नहीं करेगा।
- साइड-फेस को सेंटर में करें, सभी कैरेक्टर्स का मुंह एक ही दिशा में रखें। चेहरे के आगे आ रहे किसी भी ऑब्जेक्ट को हटाएं।

🚨 कड़ा टेक्स्ट व टाइपोग्राफी निर्देश (STRICT TEXT PLACEMENT & SIZING RULES):
1. 100% सीधा टेक्स्ट: सभी टेक्स्ट बिल्कुल सीधे (Perfect Horizontal & Straight) होंगे। कोई भी टेक्स्ट टेढ़ा (No Tilted/Skewed), तिरछा या घुमावदार (No Curved Text) बिल्कुल नहीं होना चाहिए।
2. टेक्स्ट का सटीक पदानुक्रम (Size Hierarchy):
   - टॉप (10% से 18%): हेडिंग (लाइन 1 व 2) - बोल्ड 3D मैटेलिक फॉन्ट, बड़े आकार में (Primary Headline, 100% Scale)।
   - उसके नीचे: सब-हेडिंग (लाइन 3) - मीडियम आकार, हाई-कंट्रास्ट और साफ़ पढ़ने योग्य (70% Scale)।
   - मध्य भाग: तस्वीरें प्रोफेशनल तरीके से व्यवस्थित। टेक्स्ट कभी भी चेहरे के ऊपर ओवरलैप न हो।
   - तस्वीरों के नीचे: स्टोरी सारांश (लाइन 4) - साफ़ और संतुलित अक्षरों में (50% Scale, 20-25 शब्द)।
   - बॉटम: कॉल-टू-एक्शन (लाइन 5) - आई-कैचिंग बटन स्ट्रिप स्टाइल में, छोटा लेकिन स्पष्ट क्लीकेबल (40% Scale)।
3. सेफ़ मार्जिन: बाएं-दाएं और ऊपर-नीचे 8% सेफ़ स्पेस छोड़ें ताकि Facebook UI बटन टेक्स्ट को न काटें।
4. शुद्ध शब्द: इनपुट में जितना टेक्स्ट दिया है अक्षरशः सिर्फ उतना ही लिखें, कोई एक्स्ट्रा शब्द या लेबल न जोड़ें।

Color palette: Crimson Flame (#9B111E), Royal Gold (#FFD700), Pearl White (#FDFBF7)

फोटो पर लिखने वाला टेक्स्ट:
""",

    2: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), फिल्मी पोस्टर स्टाइल।

चेहरा व एक्सप्रेशन 100% लॉक:
- दी गई तस्वीरों का असली चेहरा और ओरिजिनल फेशियल एक्सप्रेशन 100% लॉक रखें।
- AI कलाकार के चेहरे, फेशियल स्ट्रक्चर या एक्सप्रेशन में कोई भी बदलाव नहीं करेगा।
- अगर बॉडी बनाने की जरूरत पड़े तो चेहरे के उसी ओरिजिनल एक्सप्रेशन के हिसाब से ही स्वाभाविक बॉडी पोस्चर बनाएं।

🚨 कड़ा टेक्स्ट व टाइपोग्राफी निर्देश (STRICT TEXT PLACEMENT & SIZING RULES):
1. 100% सीधा टेक्स्ट: सभी पंक्तियाँ 100% क्षैतिज (Strictly Horizontal) और सीधी होनी चाहिए। कोई भी अक्षर टेढ़ा, तिरछा या ढलान वाला नहीं होगा।
2. 2-कॉलम लेआउट व टेक्स्ट पदानुक्रम:
   - टॉप (10% ऊंचाई): हेडिंग व तारीख (लाइन 1 व 2) - सेंटर-अलाइन, बोल्ड मैटेलिक अक्षरों में (Primary Title)।
   - उसके नीचे: मुख्य उपशीर्षक (लाइन 3) - सेंटर-अलाइन, हाई-कंट्रास्ट (Sub-headline)।
   - लेआउट विभाजन: लेफ्ट साइड में अल्ट्रा HD तस्वीरें (कमर तक) और राइट साइड में सभी 5 बुलेट पॉइंट्स।
   - राइट साइड बुलेट पॉइंट्स (लाइनें 4 से 8): 1 से लेकर 5 तक के स्पष्ट बोल्ड नंबर (1., 2., 3., 4., 5.) के साथ, लेफ्ट-अलाइन, मीडियम साफ़ पठनीय फॉन्ट (50% Scale)।
   - बॉटम: कॉल-टू-एक्शन (अंतिम लाइन) - सेंटर-अलाइन, डार्क बैकड्रॉप पट्टी पर स्पष्ट रूप से उभरा हुआ।
3. सेफ़ मार्जिन: दोनों किनारों से 8% सेफ़ स्पेस रखें। टेक्स्ट फोटो के चेहरों को बिल्कुल न ढके।
4. शुद्ध शब्द: इनपुट में दिए गए शब्दों के अलावा कोई भी काल्पनिक शब्द न जोड़ें।

Color palette: Midnight Navy (#0B132B), Fiery Amber (#F77F00), Crisp Ivory (#FFFFFF)

फोटो पर लिखने वाला टेक्स्ट:
""",

    3: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), सस्पेंस थ्रिलर पोस्टर।

चेहरा व एक्सप्रेशन 100% लॉक:
- अनुपमा और मुख्य किरदारों का असली चेहरा और ओरिजिनल एक्सप्रेशन 100% लॉक रखें।
- AI फेशियल स्ट्रक्चर या एक्सप्रेशन में कोई बदलाव नहीं करेगा।

🚨 कड़ा टेक्स्ट व टाइपोग्राफी निर्देश (STRICT TEXT PLACEMENT & SIZING RULES):
1. 100% सीधा टेक्स्ट: कोई भी अक्षर टेढ़ा, तिरछा या ढलान वाला नहीं होगा।
2. 2-कॉलम लेआउट व टेक्स्ट पदानुक्रम:
   - टॉप (10% ऊंचाई): हेडिंग व सब-हेडिंग (लाइन 1 व 2) - बोल्ड मैटेलिक अक्षरों में (Primary Title)।
   - उसके नीचे: मुख्य महा-हेडिंग (लाइन 3) - सेंटर-अलाइन, हाई-कंट्रास्ट।
   - लेआउट: लेफ्ट साइड में सस्पेंस से भरी अल्ट्रा HD तस्वीरें और राइट साइड में सभी 5 अपकमिंग ट्विस्ट्स।
   - राइट साइड ट्विस्ट्स (लाइनें 4 से 8): 1 से लेकर 5 तक के स्पष्ट बोल्ड नंबर (1., 2., 3., 4., 5.) के साथ, लेफ्ट-अलाइन (50% Scale)।
   - बॉटम: कॉल-टू-एक्शन (लाइन 9) - सेंटर-अलाइन, आई-कैचिंग पट्टी पर।
3. सेफ़ मार्जिन: 8% सेफ़ स्पेस।
4. शुद्ध शब्द: इनपुट में जितना टेक्स्ट दिया है सिर्फ वही लिखें।

Color palette: Deep Amethyst (#240046), Electric Gold (#FFD000), Pure White (#FFFFFF)

फोटो पर लिखने वाला टेक्स्ट:
""",

    4: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), टीवी ब्रेकिंग न्यूज़ ग्राफिक्स स्टाइल।

चेहरा व एक्सप्रेशन 100% लॉक:
- अनुपमा का असली चेहरा और आक्रामक/गंभीर ओरिजिनल एक्सप्रेशन 100% लॉक रखें।
- AI फेशियल स्ट्रक्चर या एक्सप्रेशन में कोई बदलाव नहीं करेगा।

🚨 कड़ा टेक्स्ट व टाइपोग्राफी निर्देश:
1. टॉप पर रेड/येलो 3D ब्रेकिंग न्यूज़ स्ट्रिप (लाइन 1 व 2)।
2. मुख्य हेडलाइन बोल्ड, इम्पैक्टफुल (लाइन 3 व 4)।
3. बॉटम में जनता से तीखा सवाल (लाइन 5)।
4. 100% सीधा टेक्स्ट, 8% सेफ़ मार्जिन।

Color palette: Breaking Red (#D90429), Warning Yellow (#FFCC00), Midnight Black (#101010)

फोटो पर लिखने वाला टेक्स्ट:
""",

    5: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), हाई-ड्रामा एंगर ट्रिगर स्टाइल।

चेहरा व एक्सप्रेशन 100% लॉक:
- मुख्य किरदारों का गुस्से या ड्रामा से भरा असली चेहरा और फेशियल एक्सप्रेशन 100% लॉक रखें।
- AI फेशियल स्ट्रक्चर या एक्सप्रेशन में कोई बदलाव नहीं करेगा।

🚨 कड़ा टेक्स्ट व टाइपोग्राफी निर्देश:
- टॉप बोल्ड आक्रोश हेडलाइन (लाइन 1 व 2)।
- मिडिल में घटना का कड़वा सच (लाइन 3)।
- बॉटम में तीखा निर्णायक सवाल (लाइन 4)।
- 100% सीधा टेक्स्ट, कोई फालतू लेबल नहीं।

Color palette: Blood Crimson (#8B0000), Charcoal Gray (#1E1E24), Bright White (#FFFFFF)

फोटो पर लिखने वाला टेक्स्ट:
""",

    6: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), डीप इमोशनल स्टाइल।

चेहरा व एक्सप्रेशन 100% लॉक:
- अनुपमा और पीड़ित किरदारों का मार्मिक, भावुक और सच्चा असली चेहरा 100% लॉक रखें।
- AI फेशियल स्ट्रक्चर या एक्सप्रेशन में कोई बदलाव नहीं करेगा।

🚨 कड़ा टेक्स्ट व टाइपोग्राफी निर्देश:
- टॉप पर दिल को छूने वाला कोट (लाइन 1)।
- बीच में मार्मिक सच (लाइन 2 व 3)।
- नीचे संवेदनशील सवाल (लाइन 4)।
- 100% सीधा हॉरिजॉन्टल टेक्स्ट।

Color palette: Deep Teal (#005F73), Soft Amber (#EE9B00), Cream Mist (#F8F9FA)

फोटो पर लिखने वाला टेक्स्ट:
""",

    7: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), 2-कैरेक्टर फेस-ऑफ क्लैश।

चेहरा व एक्सप्रेशन 100% लॉक:
- दोनों किरदारों के आमने-सामने के असली चेहरे और आक्रामक एक्सप्रेशन्स 100% लॉक रखें।

🚨 कड़ा टेक्स्ट निर्देश (Double Speech Bubbles):
- लेफ्ट किरदार के सिर के पास डायलॉग बबल (लाइन 1)।
- राइट किरदार के सिर के पास पलटवार डायलॉग बबल (लाइन 2)।
- बॉटम में 1 निर्णायक सवाल: इन दोनों में से कौन सही है?
- 100% सीधा टेक्स्ट।

Color palette: Electric Blue (#0077B6), Fiery Orange (#E85D04), Pure White (#FFFFFF)

फोटो पर लिखने वाला टेक्स्ट:
""",

    8: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), 2-कैरेक्टर व्यंग्य व रोस्ट स्टाइल।

चेहरा व एक्सप्रेशन 100% लॉक:
- दोनों किरदारों के व्यंग्यात्मक, हैरान या रोस्ट वाले चेहरे 100% लॉक रखें।

🚨 कड़ा टेक्स्ट निर्देश (Double Speech Bubbles):
- घमंड भरा ताना डायलॉग बबल (लाइन 1)।
- मुंहतोड़ रोस्ट जवाब डायलॉग बबल (लाइन 2)।
- बॉटम में 1 चुटीला सवाल।
- 100% सीधा टेक्स्ट।

Color palette: Toxic Green (#2D6A4F), Vibrant Amber (#FFBA08), Deep Slate (#212529)

फोटो पर लिखने वाला टेक्स्ट:
""",

    9: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), न्यूज़ एजेंसी स्पेशल पोल ग्राफ़िक्स।

चेहरा व एक्सप्रेशन 100% लॉक:
- विषय से जुड़े मुख्य किरदारों के आधिकारिक, गंभीर चेहरे 100% लॉक रखें।

🚨 कड़ा टेक्स्ट निर्देश:
- टॉप पर 'न्यूज़ एजेंसी स्पेशल पोल' बैज।
- बीच में बड़ा नैतिक/पारिवारिक सवाल।
- विकल्प A और विकल्प B बड़े बॉक्स में साफ़ पठनीय।
- बॉटम में CTA: अपनी राय कमेंट में दर्ज करें।

Color palette: Royal Navy (#1D3557), Gold Accent (#E9C46A), Snow White (#F1FAEE)

फोटो पर लिखने वाला टेक्स्ट:
""",

    10: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), जनता की अदालत पोल ग्राफ़िक्स।

चेहरा व एक्सप्रेशन 100% लॉक:
- दोनों पक्षों के किरदारों के चेहरे 100% लॉक रखें।

🚨 कड़ा टेक्स्ट निर्देश:
- टॉप पर 'जनता की अदालत पोल'।
- बड़ा धर्मसंकट वाला सवाल।
- विकल्प A और विकल्प B स्पष्ट।
- बॉटम में वोटिंग कॉल।

Color palette: Rich Burgundy (#581845), Radiant Marigold (#FFC300), Clean Ivory (#FFFFFF)

फोटो पर लिखने वाला टेक्स्ट:
""",

    11: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), सिंगल कैरेक्टर अपील (अनुपमा)।

चेहरा व एक्सप्रेशन 100% लॉक:
- अनुपमा का क्लोज़-अप, कैमरे की तरफ सीधे देखते हुए आत्ममंथन या बेबसी भरा चेहरा 100% लॉक रखें।

🚨 कड़ा टेक्स्ट निर्देश (Single Speech Bubble):
- बड़ा उद्धरण चिन्ह (Quotes) के साथ दिल की पुकार।
- बॉटम में सवाल: क्या मेरा फैसला गलत था?
- 100% सीधा टेक्स्ट।

Color palette: Deep Indigo (#1F2041), Sunset Coral (#FF6F59), Soft Cream (#F5F5F5)

फोटो पर लिखने वाला टेक्स्ट:
""",

    12: """8K अल्ट्रा-शार्प सिनेमैटिक Facebook पोस्ट डिज़ाइन, 1080×1350px (4:5), विरोधी किरदार का पक्ष।

चेहरा व एक्सप्रेशन 100% लॉक:
- विरोधी किरदार (लीला बा/तोषू/पाखी/प्रेरणा) का आक्रामक या अपना पक्ष रखता क्लोज़-अप चेहरा 100% लॉक रखें।

🚨 कड़ा टेक्स्ट निर्देश (Single Speech Bubble):
- किरदार का दर्शकों से सीधा तीखा व कड़वा सवाल।
- बॉटम में सवाल: क्या आप इनकी बात से सहमत हैं?
- 100% सीधा टेक्स्ट।

Color palette: Dark Olive (#333D29), Fiery Ochre (#C77DFF), Bright White (#FFFFFF)

फोटो पर लिखने वाला टेक्स्ट:
"""
}

POST_TITLES = {
    1: "Post 01 - D Full Story (4-लेयर पोस्टर)",
    2: "Post 02 - DT FULL POST (5 बुलेट स्टाइल)",
    3: "Post 03 - 5 अपकमिंग ट्विस्ट्स पोस्टर",
    4: "Post 04 - ब्रेकिंग न्यूज़ पोस्टर",
    5: "Post 05 - गुस्सा भड़काने वाला / ड्रामा",
    6: "Post 06 - भावुक करने वाला / इमोशनल",
    7: "Post 07 - डबल स्पीच बबल बहस पोस्ट",
    8: "Post 08 - डबल स्पीच बबल रोस्ट",
    9: "Post 09 - न्यूज़ एजेंसी POLL पोस्ट 1",
    10: "Post 10 - न्यूज़ एजेंसी POLL पोस्ट 2",
    11: "Post 11 - सिंगल स्पीच बबल पोस्ट 1 (अनुपमा का सवाल)",
    12: "Post 12 - सिंगल स्पीच बबल पोस्ट 2 (विरोधी पक्ष का सवाल)"
}

def parse_posts_from_gemini(content: str) -> dict:
    """Parses photo text and caption for posts 1 to 12 from Gemini output."""
    posts_data = {}
    sections = re.split(r'---\s*\n', content)
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        m = re.search(r'\[(?:पेज \d+ - )?पोस्ट (\d+)\]\s*:\s*(.*?)(?:\n|---)', sec)
        if m:
            p_num = int(m.group(1))
            photo_m = re.search(r'फोटो में लिखने के लिए टेक्स्ट:?\s*(.*?)(?=\[|$|फेसबुक कैप्शन)', sec, re.DOTALL)
            photo_text = photo_m.group(1).strip() if photo_m else ''
            
            cap_m = re.search(r'फेसबुक कैप्शन:?\s*(.*?)(?=\n---|#|\Z)', sec, re.DOTALL)
            caption = cap_m.group(1).strip() if cap_m else ''
            tags = re.findall(r'#\w+', sec)
            if tags:
                caption += '\n\n' + ' '.join(tags)

            posts_data[p_num] = {
                "photo_text": photo_text,
                "caption": caption
            }
    return posts_data

def build_all_cards(gemini_text: str, today_title: str, today_story: str, date_str: str) -> tuple:
    """
    Constructs the list of cards for Firestore.
    Returns (cards_list, category_name, today_tag, video_content, polls_content)
    """
    dt = datetime.now()
    short_date = dt.strftime("%d %b %Y")
    tag_date = dt.strftime("%d%b").lower()

    combined_text = f"{today_title} {date_str}"
    m = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})', combined_text)
    if m:
        day = m.group(1).zfill(2)
        mon = m.group(2)[:3].capitalize()
        year = m.group(3)
        short_date = f"{day} {mon} {year}"
        tag_date = f"{day}{mon.lower()}"

    category_name = f"📅 {short_date} - अनुपमा 12 पोस्ट्स"
    today_tag = f"anu_card_{tag_date}"

    # Extract Video 1 & Polls
    vid_m = re.search(r'---\s*\[वीडियो 1\](.*?)(?=\n---\s*\[|\Z)', gemini_text, re.DOTALL)
    video_content = vid_m.group(1).strip() if vid_m else ""

    poll_m = re.search(r'---\s*\[फेसबुक पोल्स\](.*?)(?=\n---\s*\[|\Z)', gemini_text, re.DOTALL)
    polls_content = poll_m.group(1).strip() if poll_m else ""

    posts_data = parse_posts_from_gemini(gemini_text)

    # Load viral ideas note if available
    viral_ideas_prompt = ""
    viral_path = "viral_post_ideas_beyond_12.md"
    if os.path.exists(viral_path):
        try:
            with open(viral_path, "r", encoding="utf-8") as f:
                viral_ideas_prompt = f.read()
        except Exception:
            pass

    cards = []

    # Card -3: Today Written Update
    card_minus_3 = {
        "num": -3,
        "id": f"{today_tag}_note_today_written_update",
        "title": "📖 आज का लिखित अपडेट (वेबसाइट से कॉपी - NotebookLM हेतु)",
        "isNote": True,
        "prompt": f"""╔══════════════════════════════════════════════════════════════════════════════╗
║  📖 आज का लिखित अपडेट : सीधे JustShowBiz वेबसाइट से कॉपी किया गया कंटेंट      ║
║  📅 {short_date} | NotebookLM में नया सोर्स जोड़ने के लिए यहाँ से कॉपी करें     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📌 निर्देश: नीचे दिए गए पूरे टेक्स्ट को कॉपी करें और अपने मोबाइल या लैपटॉप में खुले NotebookLM में 'Add Source' ➔ 'Copied Text' करके पेस्ट कर दें।

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{today_title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{today_story}
""",
        "photoText": today_title,
        "caption": "NotebookLM में सोर्स डालने के लिए इस नोट को कॉपी करें।"
    }
    cards.append(card_minus_3)

    # Card 00: Viral Ideas Note
    if viral_ideas_prompt:
        card_zero = {
            "num": 0,
            "id": f"{today_tag}_note_viral_ideas",
            "title": "📝 स्पेशल नोट 3: 12+ नए वायरल पोस्ट आइडियाज (Viral Concepts Beyond 12)",
            "isNote": True,
            "prompt": viral_ideas_prompt,
            "photoText": "",
            "caption": "12 अतिरिक्त वायरल पोस्ट्स (Viral Concepts Directory)"
        }
        cards.append(card_zero)

    # Cards 1 to 12
    for num in range(1, 13):
        p_info = posts_data.get(num, {"photo_text": "", "caption": ""})
        p_text = p_info["photo_text"]
        p_cap = p_info["caption"]
        template = CARD_PROMPT_TEMPLATES.get(num, "")
        full_prompt = f"{template}\n{p_text}" if p_text else template

        card = {
            "num": num,
            "id": f"{today_tag}_post_{num:02d}",
            "title": POST_TITLES.get(num, f"Post {num:02d}"),
            "prompt": full_prompt,
            "photoText": p_text,
            "caption": p_cap
        }
        cards.append(card)

    return cards, category_name, today_tag, video_content, polls_content

def push_cards_to_firestore(cards: list, category_name: str) -> int:
    """DISABLED: Individual prompt cards are permanently disabled per user mandate. Only 5 clean Note Tiles are allowed."""
    print("⚠️ Notice: Individual card publishing is permanently DISABLED per user mandate. Only 5 Note Tiles are published.")
    return 0


def clean_photo_text(raw_text: str) -> str:
    """Cleans technical labels and markdown stars from photo text for Note 4."""
    if not raw_text:
        return ""
    # Strip markdown bold/stars
    text = re.sub(r'\*+', '', raw_text)
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove label prefixes like 'हेडिंग:', 'सबहेडिंग:', 'डायलॉग 1:', 'बुलेट 1:', 'कॉल-टू-एक्शन:', 'सीटीए:', 'CTA:'
        line = re.sub(
            r'^(?:हेडिंग\s*\d*|सबहेडिंग|मुख्य\s*हेडिंग|डायलॉग\s*\d*|बुलेट\s*\d*|कॉल-टू-एक्शन|सीटीए|CTA|लाइन\s*\d*|पॉइंट\s*\d*)\s*[:：\-]\s*',
            '',
            line,
            flags=re.IGNORECASE
        )
        line = line.strip()
        if line:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def build_all_photo_texts_note(posts_data: dict, short_date: str, episode_title: str) -> str:
    """Builds the comprehensive, decorated Note 4 containing all 12 photo texts cleanly."""
    header = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║  🖼️ अनुपमा — आज के सभी 12 फोटो पर लिखे जाने वाले शुद्ध टेक्स्ट               ║
║  📅 {short_date} | एपिसोड: {episode_title}                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

📌 निर्देश: इन 12 पोस्ट्स के फोटो टेक्स्ट को आप सीधे अपनी फोटो/इमेज डिज़ाइन में इस्तेमाल कर सकते हैं।
"""
    blocks = [header]
    for num in range(1, 13):
        title = POST_TITLES.get(num, f"पोस्ट {num:02d}")
        raw_p = posts_data.get(num, {}).get("photo_text", "")
        cleaned = clean_photo_text(raw_p)
        block = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📸 [{title}]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{cleaned}
"""
        blocks.append(block)
    return "\n".join(blocks)


def push_five_notes_to_app(category_name: str, today_tag: str, short_date: str, episode_title: str, story_text: str, video_content: str, polls_content: str, posts_data: dict) -> int:
    """
    Publishes strictly the 5 clean Note Tiles to Firestore for Prompt App.
    Ensures that ALL cards in the category have isNote: True so Prompt App renders
    the clean 5-tile note box grid without any individual prompt card clutter.
    """
    now_ms = str(int(time.time() * 1000))

    # Note -3: Full Written Update (NotebookLM)
    note_minus_3_content = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║  📖 आज का लिखित अपडेट : सीधे JustShowBiz वेबसाइट से कॉपी किया गया कंटेंट      ║
║  📅 {short_date} | NotebookLM में नया सोर्स जोड़ने के लिए यहाँ से कॉपी करें     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📌 निर्देश: नीचे दिए गए पूरे टेक्स्ट को कॉपी करें और अपने मोबाइल या लैपटॉप में खुले NotebookLM में 'Add Source' ➔ 'Copied Text' करके पेस्ट कर दें।

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{episode_title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{story_text}
"""

    # Note 0: 12 Fresh Viral Post Ideas (guaranteed 365-day annual non-repeating directly from story)
    try:
        from viral_ideas_tracker import build_decorated_viral_ideas_note
        viral_ideas_text, _ = build_decorated_viral_ideas_note(short_date, episode_title, story_text=story_text)
    except Exception as e:
        print(f"Viral tracker fallback: {e}")
        viral_ideas_text = "12 वायरल पोस्ट आइडियाज"

    # Note 1: All 12 Photo Texts Compiled Cleanly
    all_photo_texts_content = build_all_photo_texts_note(posts_data, short_date, episode_title)

    five_notes = [
        {
            "id": f"{today_tag}_note_today_written_update",
            "title": "📖 आज का लिखित अपडेट (वेबसाइट से कॉपी - NotebookLM हेतु)",
            "prompt": note_minus_3_content,
            "order": -3
        },
        {
            "id": f"{today_tag}_note_video_vo",
            "title": "🎬 स्पेशल नोट 1: 3 मिनट लॉन्ग वीडियो व वॉइसओवर स्क्रिप्ट",
            "prompt": video_content,
            "order": -2
        },
        {
            "id": f"{today_tag}_note_polls",
            "title": "📊 स्पेशल नोट 2: 5 फेसबुक पोल पोस्ट्स",
            "prompt": polls_content,
            "order": -1
        },
        {
            "id": f"{today_tag}_note_viral_ideas",
            "title": "📝 स्पेशल नोट 3: 12+ नए वायरल पोस्ट आइडियाज (Viral Concepts Beyond 12)",
            "prompt": viral_ideas_text,
            "order": 0
        },
        {
            "id": f"{today_tag}_note_all_photo_texts",
            "title": "🖼️ स्पेशल नोट 4: सभी 12 फोटो पर लिखे जाने वाले टेक्स्ट",
            "prompt": all_photo_texts_content,
            "order": 1
        }
    ]

    print("=" * 60)
    print(f"🚀 Publishing 5 Clean Note Tiles to Category: '{category_name}'")
    print("=" * 60)

    success_count = 0
    for note in five_notes:
        doc_id = note["id"]
        title = note["title"]
        order_num = note["order"]
        prompt = note["prompt"]

        payload = {
            "fields": {
                "id": {"stringValue": doc_id},
                "title": {"stringValue": title},
                "category": {"stringValue": category_name},
                "basePrompt": {"stringValue": prompt},
                "photoText": {"stringValue": title},
                "caption": {"stringValue": title},
                "order": {"integerValue": str(order_num)},
                "isNote": {"booleanValue": True},
                "createdAt": {"integerValue": now_ms},
                "updatedAt": {"integerValue": now_ms},
                "layers": {"arrayValue": {"values": []}}
            }
        }

        url = f"{FIRESTORE_CARDS_URL}/{doc_id}?key={FIREBASE_API_KEY}"
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"}, method="PATCH")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                print(f"✅ Note Tile [Order {order_num:>2}]: '{title}' successfully published!")
                success_count += 1
        except Exception as e:
            print(f"❌ Note Tile [Order {order_num:>2}]: '{title}' FAILED! Error: {e}")

    print(f"\n🎉 Finished: {success_count}/5 Note Tiles published under '{category_name}'!")
    return success_count


def run_daily_cards_pipeline(gemini_output_file: str = "today_gemini_output.txt") -> bool:
    """Main function to run complete cards publishing pipeline."""
    from story_scraper import fetch_latest_anupama_update
    
    print("1. Fetching today's latest Anupamaa Written Update...")
    story_data = fetch_latest_anupama_update()
    title = story_data["title"]
    story_text = story_data["story"]
    date_str = story_data["date"]
    print(f"   Episode: {title}")

    gemini_text = ""
    if os.path.exists(gemini_output_file):
        with open(gemini_output_file, "r", encoding="utf-8") as f:
            gemini_text = f.read()

    if not gemini_text or len(gemini_text) < 1000:
        print("2. Calling Gemini API to generate 12 posts structured content...")
        from gemini_api_client import generate_with_gemini_api
        gemini_text = generate_with_gemini_api(story_text, date_str)
        with open(gemini_output_file, "w", encoding="utf-8") as f:
            f.write(gemini_text)

    print(f"3. Building cards from Gemini output ({len(gemini_text)} chars)...")
    cards, category_name, today_tag, video_content, polls_content = build_all_cards(gemini_text, title, story_text, date_str)
    posts_data = parse_posts_from_gemini(gemini_text)

    # Short date e.g. "16 Sep 2026"
    m = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})', title)
    clean_date = f"{m.group(1)} {m.group(2)} {m.group(3)}" if m else datetime.now().strftime("%d %B %Y")

    print(f"4. Pushing 5 Clean Note Tiles to Firestore (No individual card clutter)...")
    count = push_five_notes_to_app(
        category_name=category_name,
        today_tag=today_tag,
        short_date=clean_date,
        episode_title=title,
        story_text=story_text,
        video_content=video_content,
        polls_content=polls_content,
        posts_data=posts_data
    )

    # 5. Sync to Google Doc with complete package (all 12 cards + scripts + polls)
    try:
        from gdocs_service import send_to_google_docs, format_master_gdoc_content
        print(f"\n5. Generating Master Google Doc via Webhook...")
        gdoc_text = format_master_gdoc_content(clean_date, polls_content, video_content, cards)
        doc_url = send_to_google_docs(f"{category_name} - संपूर्ण एपिसोड ड्राफ्ट", gdoc_text)
        if doc_url:
            print(f"✅ Master Google Doc successfully created: {doc_url}")
    except Exception as ge:
        print(f"Note: Google Doc sync note: {ge}")

    return count >= 5


def publish_all_12_cards(gemini_text: str = None, title: str = None, story_text: str = None, date_str: str = None) -> bool:
    from story_scraper import fetch_latest_anupama_update
    if not title or not story_text:
        story_data = fetch_latest_anupama_update()
        title = story_data["title"]
        story_text = story_data["story"]
        if not date_str:
            date_str = story_data.get("date", "")

    m = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})', title)
    if m:
        clean_date = f"{m.group(1)} {m.group(2)} {m.group(3)}"
    else:
        clean_date = datetime.now().strftime("%d %B %Y")

    if not gemini_text:
        from gemini_api_client import generate_with_gemini_api
        gemini_text = generate_with_gemini_api(story_text, clean_date)

    cards, category_name, today_tag, video_content, polls_content = build_all_cards(gemini_text, title, story_text, clean_date)
    posts_data = parse_posts_from_gemini(gemini_text)

    # Push strictly the 5 Note Tiles
    count = push_five_notes_to_app(
        category_name=category_name,
        today_tag=today_tag,
        short_date=clean_date,
        episode_title=title,
        story_text=story_text,
        video_content=video_content,
        polls_content=polls_content,
        posts_data=posts_data
    )

    try:
        from gdocs_service import send_to_google_docs, format_master_gdoc_content
        gdoc_text = format_master_gdoc_content(clean_date, polls_content, video_content, cards)
        send_to_google_docs(f"{category_name} - संपूर्ण एपिसोड ड्राफ्ट", gdoc_text)
    except Exception as ge:
        print(f"Google Doc sync note: {ge}")

    return count >= 5


if __name__ == "__main__":
    run_daily_cards_pipeline()

