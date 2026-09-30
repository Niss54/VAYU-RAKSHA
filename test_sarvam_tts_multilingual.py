import os
import sys
import base64

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Read API key from .env
api_key = None
for env_file in [".env", "apps/web/.env.local"]:
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("SARVAM_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val and not val.startswith("["):
                        api_key = val
                        break
    if api_key:
        break

if not api_key:
    print("ERROR: SARVAM_API_KEY not found in .env or apps/web/.env.local", file=sys.stderr)
    sys.exit(1)

import requests

TEST_LANGUAGES = [
    {
        "lang": "Hindi",
        "code": "hi-IN",
        "text": "चक्रवात से सावधान रहें। सभी तटीय निवासी तुरंत सुरक्षित आश्रय स्थलों पर पहुंचें।",
    },
    {
        "lang": "Odia",
        "code": "od-IN",
        "text": "ବାତ୍ୟା ଆସୁଛି। ସମସ୍ତ ଉପକୂଳବାସୀ ତୁରନ୍ତ ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳକୁ ଯାଆନ୍ତୁ।",
    },
    {
        "lang": "Bengali",
        "code": "bn-IN",
        "text": "ঘূর্ণিঝড় সতর্কতা: উপকূলীয় এলাকার মানুষ অবিলম্বে নিরাপদ আশ্রয়ে যান।",
    },
    {
        "lang": "Telugu",
        "code": "te-IN",
        "text": "తుఫాను హెచ్చరిక: తీరప్రాంత ప్రజలు వెంటనే సురక్షిత ప్రాంతాలకు వెళ్లండి.",
    },
    {
        "lang": "Tamil",
        "code": "ta-IN",
        "text": "புயல் எச்சரிக்கை: கடலோர மக்கள் உடனடியாக பாதுகாப்பான இடங்களுக்குச் செல்லவும்.",
    },
    {
        "lang": "English",
        "code": "en-IN",
        "text": "Urgent cyclone warning: All coastal residents must evacuate to designated storm shelters immediately.",
    },
]

print("==================================================================")
print("TESTING SARVAM AI TTS (bulbul:v2) ACROSS ALL 6 INDIAN LANGUAGES")
print("==================================================================")

url = "https://api.sarvam.ai/text-to-speech"
headers = {
    "Content-Type": "application/json",
    "api-subscription-key": api_key,
}

success_count = 0

for item in TEST_LANGUAGES:
    payload = {
        "inputs": [item["text"]],
        "target_language_code": item["code"],
        "speaker": "kavya",
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.5,
        "speech_sample_rate": 22050,
        "enable_preprocessing": True,
        "model": "bulbul:v3",
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=20)
        if res.status_code == 200:
            data = res.json()
            audios = data.get("audios", [])
            if audios and len(audios[0]) > 100:
                audio_bytes = base64.b64decode(audios[0])
                kb_size = len(audio_bytes) / 1024
                print(f"  [OK] {item['lang']:<8} ({item['code']}): Generated {kb_size:.1f} KB WAV Audio | Text: {item['text'][:40]}...")
                success_count += 1
            else:
                print(f"  [FAIL] {item['lang']} ({item['code']}): Empty audio array returned")
        else:
            print(f"  [FAIL] {item['lang']} ({item['code']}): HTTP {res.status_code} - {res.text}")
    except Exception as e:
        print(f"  [ERROR] {item['lang']} ({item['code']}): {e}")

print("==================================================================")
print(f"RESULT: {success_count}/{len(TEST_LANGUAGES)} Languages Successfully Synthesized via Sarvam AI!")
print("==================================================================")

if success_count == len(TEST_LANGUAGES):
    sys.exit(0)
else:
    sys.exit(1)
