"""
gemini_api_client.py
Official Google Gemini API client for 100% Cloud Execution.
Runs anywhere without needing a browser, cookies, or 2FA.
Generates:
1. [पोस्ट 1] फुल स्टोरी पोस्टर (फोटो टेक्स्ट + फेसबुक कैप्शन)
2. [पोस्ट 2] फुल स्टोरी (5 बुलेट पोस्टर) (फोटो टेक्स्ट + फेसबुक कैप्शन)
3. [पोस्ट 3] 5 अपकमिंग ट्विस्ट्स पोस्टर (फोटो टेक्स्ट + फेसबुक कैप्शन)
4. [पोस्ट 4] एपिसोड की सबसे बड़ी घटना (फोटो टेक्स्ट + फेसबुक कैप्शन)
5. [पोल पोस्ट्स] 2 ऑडियंस वोटिंग सवाल
6. [गहरा विश्लेषण] चरण 2 विश्लेषण
"""

import json
import urllib.request
import logging
from config import BASE_DIR

logger = logging.getLogger("AnupamaaBot.GeminiAPI")

GEMINI_API_KEY = "AQ.Ab8RN6K4JTzVlV1BmkAEyiJqQFuYdGCk3VFqNlNpgWKrd557JA"
MODEL_NAME = "gemini-flash-lite-latest"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

GEM_SYSTEM_PROMPT = """आप अनुपमा (Anupamaa) टीवी सीरियल के विशेषज्ञ कंटेंट क्रिएटर और सोशल मीडिया राइटर हैं।
नीचे दिए गए आज के एपिसोड की रिटन स्टोरी (Written Update) को पढ़कर आपको फेसबुक और इंस्टाग्राम के लिए आकर्षक, एंगेजिंग और वायरल कंटेंट तैयार करना है।

आपको निम्नलिखित फॉर्मेट का हूबहू पालन करके आउटपुट देना है:

[पोस्ट 1] : फुल स्टोरी पोस्टर
फोटो में लिखने के लिए टेक्स्ट
हेडिंग: Anupamaa
दिनांक: [आज की तारीख]
सबहेडिंग: [1 लाइन में मुख्य मोड़]
स्टोरी: [2-3 वाक्यों में आज की मुख्य कहानी]
- CTA: [1 सवाल ऑडियंस के लिए]

[पोस्ट 1] : फुल स्टोरी पोस्टर
फेसबुक कैप्शन
[विस्तृत 3-4 पैराग्राफ में दिलचस्प अंदाज में आज की कहानी]
#Anupamaa #StarPlus #AnupamaaUpcomingTwist

---

[पोस्ट 2] : फुल स्टोरी (5 बुलेट पोस्टर)
फोटो में लिखने के लिए टेक्स्ट
हेडिंग: अनुपमा
दिनांक: Today Update
सबहेडिंग 1: [1 आकर्षक लाइन]
सबहेडिंग 2: 
  • [बुलेट 1 - मुख्य घटना]
  • [बुलेट 2 - दूसरा ट्विस्ट]
  • [बुलेट 3 - भावुक पल]
  • [बुलेट 4 - नया मोड़]
  • [बुलेट 5 - बड़ा झटका]
- CTA: [ऑडियंस से सवाल]

[पोस्ट 2] : फुल स्टोरी (5 बुलेट पोस्टर)
फेसबुक कैप्शन
[मजेदार, तीखे और चुटीले अंदाज में 3-4 पैराग्राफ का कैप्शन]
#AnupamaaRoast #ShahFamilyDrama #AnupamaaUpdate

---

[पोस्ट 3] : 5 अपकमिंग ट्विस्ट्स पोस्टर
फोटो में लिखने के लिए टेक्स्ट
हेडिंग: अनुपमा
सबहेडिंग 1: अब आगे क्या होगा? Upcoming Twists
सबहेडिंग 2: 
  • [आने वाला ट्विस्ट 1]
  • [आने वाला ट्विस्ट 2]
  • [आने वाला ट्विस्ट 3]
  • [आने वाला ट्विस्ट 4]
  • [आने वाला ट्विस्ट 5]
- CTA: [आपको किस मोड़ का इंतजार है?]

[पोस्ट 3] : 5 अपकमिंग ट्विस्ट्स पोस्टर
फेसबुक कैप्शन
[आगे आने वाले रोमांचक मोड़ों पर आधारित 3-4 पैराग्राफ का कैप्शन]
#AnupamaaTwist #AnupamaaSpoiler #StarPlus

---

[पोस्ट 4] : एपिसोड की सबसे बड़ी घटना
फोटो में लिखने के लिए टेक्स्ट
हेडिंग: [आज की सबसे सनसनीखेज हेडिंग]
सबहेडिंग: [सबहेडिंग]
स्टोरी: [आज के एपिसोड की उस 1 सबसे बड़ी घटना का विवरण]
कॉल टू एक्शन: [कमेंट में अपनी राय लिखें सवाल]

[पोस्ट 4] : एपिसोड की सबसे बड़ी घटना
फेसबुक कैप्शन
[इस बड़ी घटना पर आधारित जोरदार 3-4 पैराग्राफ कैप्शन]
#AnupamaaDrama #BigTwist #AnupamaaNews

---

Poll 1: [पहला दिलचस्प वोटिंग सवाल]
विकल्प A: [...]
विकल्प B: [...]

Poll 2: [दूसरा वोटिंग सवाल]
विकल्प A: [...]
विकल्प B: [...]

---

चरण 2: एपिसोड विश्लेषण व सोशल मीडिया एंगल
[एपिसोड के मुख्य किरदार (अनुपमा, लीला, परितोष, अंश, प्रेम) के फैसलों पर विश्लेषण, ऑडियंस का संभावित रिएक्शन और वायरल होने वाले पॉइंट्स]
"""


def generate_with_gemini_api(story_text: str, episode_date: str = "") -> str:
    """
    Calls Google Gemini API directly. Returns the full formatted multi-post response.
    """
    logger.info("Calling Google Gemini API directly (Cloud Mode)...")
    prompt_text = f"{GEM_SYSTEM_PROMPT}\n\nआज का एपिसोड टेक्स्ट:\n{story_text}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_text}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 4096
        }
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidate = data.get("candidates", [{}])[0]
            parts = candidate.get("content", {}).get("parts", [{}])
            result_text = parts[0].get("text", "").strip()
            logger.info(f"Gemini API returned {len(result_text)} chars of structured content!")
            return result_text
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        raise e
