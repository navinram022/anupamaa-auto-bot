# -*- coding: utf-8 -*-
"""
push_video_and_poll_notes.py
Pushes:
1. [स्पेशल नोट 1] 3 मिनट लॉन्ग वीडियो व वॉइसओवर स्क्रिप्ट (14 Sep 2026)
2. [स्पेशल नोट 2] 5 फेसबुक पोल पोस्ट्स (14 Sep 2026)
Directly into:
- Category Folder: '📅 14 Sep 2026 - अनुपमा 12 पोस्ट्स' as individual Note Tiles (isNote: True)
- Notebook Notes: app_meta/notes
"""

import sys
import time
import json
import socket
import urllib.request
import urllib.error

# Force IPv4 resolution to prevent Windows IPv6 connection timeouts
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(*args, **kwargs):
    results = _orig_getaddrinfo(*args, **kwargs)
    ipv4 = [r for r in results if r[0] == socket.AF_INET]
    return ipv4 if ipv4 else results
socket.getaddrinfo = _ipv4_getaddrinfo

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

FIREBASE_PROJECT_ID = "neetu-prompts"
FIREBASE_API_KEY = "AIzaSyD5gZr4s10roOThEeQjleJ5Sq7_rO6bA8E"
FIRESTORE_CARDS_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/prompt_cards"
FIRESTORE_NOTES_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/app_meta/notes?key={FIREBASE_API_KEY}"

CATEGORY_NAME = "📅 14 Sep 2026 - अनुपमा 12 पोस्ट्स"
DATE_STR = "14 September 2026"
TODAY_TAG = "14sep"

VIDEO_NOTE_CONTENT = """╔══════════════════════════════════════════════════════════════════════════════╗
║  🎬 3 मिनट लॉन्ग वीडियो : पूरी कहानी का सिलसिलेवार विश्लेषण व वॉइसओवर स्क्रिप्ट   ║
║  📅 14 September 2026 | अनुपमा महा-एपिसोड                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 [भाग A] : 16:9 YouTube / Facebook वीडियो थंबनेल निर्देश (1920×1080px)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- थंबनेल साइज: 16:9 Landscape (1920×1080px)
- सीन: (बाएं 60% में बिल्डर दफ्तर के बाहर खुदकुशी कर रहे बुजुर्ग को बचाती शेरनी अनुपमा, दाएं 40% में शाह हाउस में जश्न मनाते तोषू-पाखी और फटकारते बापूजी)
- थंबनेल मुख्य हेडिंग: बिल्डर फ्रॉड पर अनुपमा का महा-विद्रोह!
- थंबनेल सबहेडिंग: खुदकुशी कर रहे पीड़ित को बचाया, फूंक दिया आंदोलन का बिगुल!
- थंबनेल हुक: जनता जनार्दन बदलेगी सरकार, भ्रष्ट बिल्डर जाएगा सलाखों के पीछे!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎙️ [भाग B] : 3 मिनट की सिलसिलेवार वॉइसओवर स्क्रिप्ट (पूरी कहानी का रोमांचक सार)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

दोस्तों! आज अनुपमा के एपिसोड में ऐसा रोंगटे खड़े कर देने वाला महा-ड्रामा देखने को मिला, जहां एक तरफ शाह हाउस में बेशर्मी का जश्न मन रहा था, तो दूसरी तरफ बिल्डर के दफ्तर के बाहर जिंदगी और मौत का महा-संग्राम छिड़ गया! एपिसोड की शुरुआत में अनुपमा अपने उजड़े हुए आशियाने के लिए फूट-फूट कर रोती है और दिग्विजय उसकी बेबसी देखकर भावुक हो जाता है। शाह हाउस में इशानी और अंश इस फ्रॉड पर चर्चा करते हैं। इशानी अनुपमा की मदद के लिए अपने हिस्से के पैसे देने का फैसला करती है, लेकिन अंश कहता है कि बात सिर्फ पैसों की नहीं बल्कि टूटे हुए भरोसे की है।

तभी शाह हाउस में तोषू और पाखी अनुपमा के पैसे डूबने पर बेशर्मों की तरह तालियां बजाकर जश्न मनाने लगते हैं! यह देखकर बापूजी का गुस्सा सातवें आसमान पर पहुंच जाता है। बापूजी दोनों को कड़ी फटकार लगाते हैं और कहते हैं कि अगर अपनी सगी मां की बर्बादी पर जश्न मनाना है तो घर के बाहर जाकर मनाओ, यहां नहीं! उधर प्रेरणा अंश पर दबाव बनाती है कि भले ही समय गलत है लेकिन उन्हें अपने नए घर की डाउन पेमेंट अभी करनी होगी। लेकिन अंश अपनी मां के दुख में उसके साथ खड़े रहने का फैसला करता है और प्रेरणा की बात सुनने से साफ इनकार कर देता है।

इसके बाद जब अनुपमा और दिग्विजय बिल्डर के दफ्तर पहुंचते हैं, तो वहां पहले से ही ठगे गए खरीदारों का उग्र प्रदर्शन चल रहा होता है। लोग अपनी जिंदगीभर की गाढ़ी कमाई डूबने पर रो-बिलख रहे होते हैं। तभी एक बेबस बुजुर्ग अपनी पूरी जमा-पूंजी लुट जाने के गम में अपनी जान देने की कोशिश करता है! अनुपमा अपनी जान पर खेलकर उस बुजुर्ग को रोकती है और उसे सीने से लगाकर कहती है कि किसी भी इंसान की अनमोल जिंदगी इस धोखेबाज बिल्डर के फ्रॉड से छोटी नहीं हो सकती! अनुपमा सभी पीड़ितों को अपने हक के लिए लड़ने की प्रेरणा देती है और पुलिस प्रशासन को सख्त चेतावनी देती है कि ऐसे ठग बिल्डर गरीबों की कमाई लूटकर विदेश भाग जाते हैं, पुलिस तुरंत एक्शन ले! अनुपमा ऐलान करती है कि जब एक आम इंसान के पास खोने को कुछ नहीं बचता, तो वो सरकारें तक हिला सकता है, इसीलिए उसे जनता जनार्दन कहते हैं! पूरी भीड़ अनुपमा के समर्थन में खड़ी हो जाती है।

उधर शाह हाउस में तोषू और पाखी बा के कान भरते हैं कि बापूजी घर बेचकर अनुपमा की मदद कर देंगे। लेकिन लीला बा का जवाब सुनकर दोनों के होश उड़ जाते हैं! बा कहती हैं कि अच्छा हुआ अनुपमा के पैसे डूब गए, अब वह इसी घर में रहकर मेरी सेवा करेगी! तोषू और पाखी भी सोचते हैं कि बा तो उनसे भी बड़ी स्वार्थी निकलीं!

और दोस्तों, प्रीकैप में तो दिल छू लेने वाला पल आया जब कैटरिंग के दौरान राही एक पिता-बेटी को देखकर अनुज को याद करके रो पड़ी। अनुपमा ने उसे गले लगाकर भरोसा दिलाया कि एक दिन अनुज अचानक सबके सामने जरूर लौट आएगा!

अब सवाल सिर्फ इतना है कि क्या अनुपमा का यह जन-आंदोलन भ्रष्ट बिल्डरों को जेल पहुंचा पाएगा? और क्या लीला बा का यह स्वार्थ शाह हाउस को बर्बाद कर देगा? अपनी राय कमेंट में जरूर बताएं!"""

POLLS_NOTE_CONTENT = """╔══════════════════════════════════════════════════════════════════════════════╗
║  📊 5 फेसबुक पोल पोस्ट्स : हाई-एंगेजमेंट ऑडियंस वोटिंग व डिबेट सवाल             ║
║  📅 14 September 2026 | सीधा फेसबुक पोल फीचर में कॉपी-पेस्ट करने हेतु          ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗳️ [पोल 01] : तोषू-पाखी का जश्न vs बापूजी की फटकार (पारिवारिक नैतिकता)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
मुद्दा: माँ के 5 लाख डूबने पर तोषू और पाखी का जश्न मनाना
सवाल: माँ के 5 लाख डूबने पर तोषू और पाखी का जश्न मनाना क्या इस बात का सबूत है कि शाह हाउस के बच्चों की इंसानियत पूरी तरह मर चुकी है?

विकल्प A: हाँ, सगी माँ की बर्बादी पर तालियाँ बजाने वाले बच्चे औलाद कहलाने लायक नहीं हैं।
विकल्प B: नहीं, यह उनका पुराना पारिवारिक बदला है, उन्होंने अनुपमा को पहले ही चेताया था।

👉 कॉल टू एक्शन (CTA): कमेंट में अपना वोट दर्ज करें!
#AnupamaaPoll #ShahHouseDrama #ToshuPakhiExposed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗳️ [पोल 02] : लीला बा का चौंकाने वाला स्वार्थ (बुढ़ापे की सुरक्षा vs असंवेदनशीलता)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
मुद्दा: शाह हाउस में बा का बयान कि 'अच्छा हुआ अनुपमा लुट गई'
सवाल: लीला बा का यह कहना कि 'अच्छा हुआ अनुपमा का नुकसान हो गया, अब वो इसी घर में रहकर सेवा करेगी'—क्या यह बा का हद दर्जे का स्वार्थ है?

विकल्प A: 100% स्वार्थ और संवेदनहीनता! माँ के रूप में ऐसी सोच बेहद शर्मनाक है।
विकल्प B: बा की व्यावहारिक सोच, वे बुढ़ापे में परिवार और घर का सहारा चाहती हैं।

👉 कॉल टू एक्शन (CTA): इस बयान पर आपकी क्या राय है? कमेंट में बताएं!
#LeelaBa #AnupamaaDebate #FamilySelfishness

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗳️ [पोल 03] : प्रेरणा की जल्दबाजी vs अंश की संजीदगी (पति-पत्नी का टकराव)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
मुद्दा: अनुपमा के नुकसान के बीच नए घर की डाउन पेमेंट का दबाव
सवाल: जब पूरा परिवार 5 लाख के फ्रॉड के सदमे में है, तब प्रेरणा का नए घर की डाउन पेमेंट के लिए अंश पर दबाव बनाना कितना जायज है?

विकल्प A: प्रेरणा सही है, अपने भविष्य और नए घर के लिए समय पर किस्त भरना जरूरी है।
विकल्प B: सरासर गलत और असंवेदनशील! दुख की घड़ी में थोड़ा इंतजार करना चाहिए था।

👉 कॉल टू एक्शन (CTA): आप किसके साथ हैं—प्रेरणा या अंश? कमेंट करें!
#AnshPrerna #FamilyCrisis #RelationshipDrama

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗳️ [पोल 04] : अनुपमा का महा-आंदोलन (सड़क की लड़ाई vs कानूनी रास्ता)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
मुद्दा: ठग बिल्डर के फरार होने पर जनता जनार्दन का मोर्चा
सवाल: ठग बिल्डर के फरार होने पर अनुपमा का सभी पीड़ितों को एकजुट करके 'जनता जनार्दन' का आंदोलन छेड़ना क्या सबसे सही कदम है?

विकल्प A: हाँ, बिल्डर और प्रशासन को झुकाने के लिए एकजुट जन-आंदोलन ही एकमात्र रास्ता है।
विकल्प B: नहीं, सीधे कोर्ट और पुलिस केस से ही कानूनी रूप से पैसा वापस मिल सकता है।

👉 कॉल टू एक्शन (CTA): आपकी नज़र में पैसा वापस पाने का सबसे ताकतवर रास्ता कौन सा है?
#JantaJanardhan #JusticeForHomeBuyers #AnupamaaAction

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗳️ [पोल 05] : अनुज कपाड़िया की वापसी का सस्पेंस (मेकर्स का बड़ा हिंट)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
मुद्दा: कैटरिंग के दौरान राही को अनुज की याद और अनुपमा का भरोसा
सवाल: कैटरिंग के दौरान राही को अनुज की याद आना और अनुपमा का कहना कि 'अनुज अचानक वापस आएगा'—क्या मेकर्स बहुत जल्द अनुज को शो में वापस ला रहे हैं?

विकल्प A: 100% हाँ! अनुज कपाड़िया की धमाकेदार वापसी के बिना शो की टीआरपी अधूरी है।
विकल्प B: नहीं, यह सिर्फ दर्शकों को बांधे रखने के लिए इमोशनल डायलॉग है।

👉 कॉल टू एक्शन (CTA): क्या आप भी अनुज कपाड़िया की वापसी का बेसब्री से इंतजार कर रहे हैं?
#AnujKapadia #MaanComeback #AnupamaaTwist"""

CARDS_TO_PUSH = [
    {
        "id": f"card_{TODAY_TAG}_note_video_01",
        "title": f"🎬 स्पेशल नोट 1: 3 मिनट लॉन्ग वीडियो व वॉइसओवर स्क्रिप्ट ({DATE_STR})",
        "order": -2,
        "isNote": True,
        "content": VIDEO_NOTE_CONTENT,
        "photoText": "3 मिनट लॉन्ग वीडियो व वॉइसओवर स्क्रिप्ट",
        "caption": f"अनुपमा {DATE_STR} - 3 मिनट यूट्यूब व फेसबुक वीडियो स्क्रिप्ट"
    },
    {
        "id": f"card_{TODAY_TAG}_note_polls_05",
        "title": f"📊 स्पेशल नोट 2: 5 फेसबुक पोल पोस्ट्स (ऑडियंस वोटिंग सवाल - {DATE_STR})",
        "order": -1,
        "isNote": True,
        "content": POLLS_NOTE_CONTENT,
        "photoText": "5 फेसबुक पोल सवाल व विकल्प",
        "caption": f"अनुपमा {DATE_STR} - 5 फेसबुक पोल सवाल"
    }
]

def push_note_cards():
    print(f"==================================================")
    print(f"🚀 Pushing 2 Special Notes to Category: '{CATEGORY_NAME}'")
    print(f"==================================================")
    
    now_ms = str(int(time.time() * 1000))
    success_count = 0

    for card in CARDS_TO_PUSH:
        doc_id = card["id"]
        title = card["title"]
        prompt = card["content"].strip()
        photo_text = card["photoText"].strip()
        order_num = card["order"]
        caption = card["caption"].strip()

        payload = {
            "fields": {
                "id": {"stringValue": doc_id},
                "title": {"stringValue": title},
                "category": {"stringValue": CATEGORY_NAME},
                "basePrompt": {"stringValue": prompt},
                "photoText": {"stringValue": photo_text},
                "caption": {"stringValue": caption},
                "order": {"integerValue": str(order_num)},
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
            with urllib.request.urlopen(req, timeout=15) as resp:
                print(f"✅ Note Card ({order_num}): '{title}' successfully saved!")
                success_count += 1
        except Exception as e:
            print(f"❌ Note Card ({order_num}): '{title}' FAILED! Error: {e}")

    return success_count == len(CARDS_TO_PUSH)

def sync_to_app_notebook():
    print(f"\n==================================================")
    print(f"📓 Syncing Notes to App Notebook ('app_meta/notes')...")
    print(f"==================================================")

    req_get = urllib.request.Request(FIRESTORE_NOTES_URL)
    existing_notes = []
    try:
        with urllib.request.urlopen(req_get, timeout=15) as resp:
            doc_data = json.loads(resp.read().decode("utf-8"))
            values = doc_data.get("fields", {}).get("notes", {}).get("arrayValue", {}).get("values", [])
            for val in values:
                m = val.get("mapValue", {}).get("fields", {})
                existing_notes.append({
                    "id": m.get("id", {}).get("stringValue", ""),
                    "title": m.get("title", {}).get("stringValue", ""),
                    "category": m.get("category", {}).get("stringValue", ""),
                    "content": m.get("content", {}).get("stringValue", ""),
                    "updatedAt": int(m.get("updatedAt", {}).get("integerValue", "0"))
                })
    except Exception as e:
        print(f"Could not load existing notebook notes: {e}")

    now_ms = int(time.time() * 1000)
    filtered = [n for n in existing_notes if TODAY_TAG not in n.get("id", "")]
    
    filtered.insert(0, {
        "id": f"note_{TODAY_TAG}_video_script",
        "title": f"🎬 [लॉन्ग वीडियो] {DATE_STR} - वॉइसओवर स्क्रिप्ट व थंबनेल",
        "category": "अनुपमा डेली वीडियो",
        "content": VIDEO_NOTE_CONTENT,
        "updatedAt": now_ms
    })
    filtered.insert(1, {
        "id": f"note_{TODAY_TAG}_fb_polls",
        "title": f"📊 [फेसबुक पोल्स] {DATE_STR} - 5 ऑडियंस वोटिंग सवाल",
        "category": "अनुपमा डेली वीडियो",
        "content": POLLS_NOTE_CONTENT,
        "updatedAt": now_ms
    })

    firestore_values = []
    for item in filtered:
        firestore_values.append({
            "mapValue": {
                "fields": {
                    "id": {"stringValue": item.get("id", "")},
                    "title": {"stringValue": item.get("title", "")},
                    "category": {"stringValue": item.get("category", "General")},
                    "content": {"stringValue": item.get("content", "")},
                    "updatedAt": {"integerValue": str(item.get("updatedAt", now_ms))}
                }
            }
        })

    payload = {
        "fields": {
            "notes": {
                "arrayValue": {
                    "values": firestore_values
                }
            }
        }
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req_patch = urllib.request.Request(
        FIRESTORE_NOTES_URL,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )

    try:
        with urllib.request.urlopen(req_patch, timeout=15) as resp:
            print(f"✅ App Notebook successfully updated with {len(filtered)} notes!")
            return True
    except Exception as e:
        print(f"❌ Failed to sync App Notebook: {e}")
        return False

if __name__ == "__main__":
    push_note_cards()
    sync_to_app_notebook()
