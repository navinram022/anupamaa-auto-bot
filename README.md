# 📺 Anupamaa Written Update AutoBot

यह एक पूरी तरह ऑटोमैटिक बॉट है जो:
1. **JustShowBiz** से आज के अनुपमा एपिसोड का पूरा लिखित अपडेट (Story) निकालता है।
2. **Google NotebookLM** (`https://notebooklm.google.com/notebook/a611b8b8-35db-4b71-9b7e-034660c3874c`) में जाकर सोर्स (Source) के तौर पर जोड़ता है।
3. **Gemini Custom Gem** (`https://gemini.google.com/gem/8fa5c07f2950`) को वह स्टोरी देकर रिज़ल्ट हासिल करता है।
4. रिज़ल्ट को सुंदर HTML रिपोर्ट बनाकर **`Navinram022@gmail.com`** पर ईमेल कर देता है।

---

## 🚀 इस्तेमाल कैसे करें (3 आसान स्टेप्स):

### स्टेप 1: सिर्फ 1 बार Google लॉगिन करें
फ़ोल्डर में मौजूद **`Setup_Google_Login.bat`** पर डबल-क्लिक करें। 
* एक Chrome विंडो खुलेगी।
* उसमें अपना वह Google अकाउंट लॉगिन कर लें जिससे NotebookLM और Gemini जुड़ा है।
* लॉगिन होने के बाद उस Chrome विंडो को बंद कर दें। (यह लॉगिन हमेशा के लिए सेव रहेगा!)

### स्टेप 2: ईमेल पासवर्ड सेट करें (वैकल्पिक पर अनुशंसित)
`email_config.json` फ़ाइल को खोलें:
```json
{
  "sender_email": "your_email@gmail.com",
  "app_password": "xxxx xxxx xxxx xxxx",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "target_email": "Navinram022@gmail.com"
}
```
* **Gmail App Password कैसे बनाएं:**
  1. अपने Google Account > Security में जाएं।
  2. "2-Step Verification" चालू करें।
  3. "App Passwords" सर्च करके एक 16-अक्षरों का पासवर्ड बनाएं और यहाँ पेस्ट कर दें।
*(अगर ईमेल कॉन्फ़िगर नहीं भी करेंगे, तब भी यह पूरा काम करेगा और रिज़ल्ट `reports/` फ़ोल्डर में HTML फ़ाइल के रूप में सेव हो जाएगा)*

### स्टेप 3: कभी भी 1-क्लिक से चलाएं
* जब भी आपको तुरंत चलाना हो: **`Run_Anupamaa_Bot.bat`** पर डबल-क्लिक करें!
* रोज़ाना अपने आप चलने के लिए: **`Install_Daily_Task.bat`** पर डबल-क्लिक कर दें (यह Windows Task Scheduler में रोज़ सुबह और कंप्यूटर चालू होते ही ऑटोमैटिक रन सेट कर देगा)।

---

## 📁 मुख्य फ़ाइलें:
* `story_scraper.py` - RSS से 1 सेकंड में स्टोरी निकालने वाला कोड
* `notebooklm_client.py` - NotebookLM में ऑटोमैटिक सोर्स डालने वाला टूल
* `gemini_client.py` - Gemini Gem से चैट करके आउटपुट लेने वाला टूल
* `email_service.py` - ईमेल भेजने वाला सर्विस
* `main.py` - सभी 4 स्टेप्स को क्रम में चलाने वाला मुख्य प्रोग्राम
* `reports/` - जनरेट हुए सभी एपिसोड्स की लोकल कॉपी
