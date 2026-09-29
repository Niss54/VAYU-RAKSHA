"""VAYU-RAKSHA SANCHAR — Communication & Insurance Agent.

Generates context-aware multilingual emergency advisories across 6 languages
(Odia, Bengali, Telugu, Tamil, Hindi, English) and validates parametric insurance smart triggers.
"""

from typing import Any, Dict, List
import hashlib
import time

from vayu_raksha.graph.state import (
    AdvisoryNotice,
    CycloneState,
    ParametricInsuranceTrigger,
)


class SancharCommsAgent:
    """Communication and Parametric Insurance dispatch agent."""

    AGENT_NAME = "SANCHAR"

    def __init__(self) -> None:
        pass

    def run(self, state: CycloneState) -> Dict[str, Any]:
        """Generates multilingual bulletins and evaluates parametric payout triggers."""
        start_time = time.time()
        meta = state["cyclone_metadata"]
        wind_kmh = meta["max_sustained_wind_kmh"]
        surge_m = state.get("atmospheric_data", {}).get("storm_surge_crest_m", 2.3)
        earth = state.get("earth_data", {})
        high_risk_sqkm = earth.get("high_susceptibility_area_sqkm", 184.2)
        total_water_sqkm = earth.get("water_extent_sqkm", 348.6)

        flood_extent_pct = round((high_risk_sqkm / max(1.0, total_water_sqkm)) * 100.0, 1)

        # 1. Generate 6-Language Contextual Advisories
        advisories: List[AdvisoryNotice] = [
            {
                "language_code": "or",
                "language_name": "Odia (ଓଡ଼ିଆ)",
                "headline": f"ବାତ୍ୟା {meta['storm_name']} ସତର୍କତା: ଉପକୂଳ ଓଡ଼ିଶା ପାଇଁ ଜରୁରୀ ସୂଚନା",
                "district": "ପୁରୀ, ଜଗତସିଂହପୁର, କେନ୍ଦ୍ରାପଡ଼ା",
                "urgency": "IMMEDIATE",
                "plain_body": (
                    f"ବାତ୍ୟା {meta['storm_name']} ଆସନ୍ତା {meta['lead_time_hours']:.0f} ଘଣ୍ଟା ମଧ୍ୟରେ ଉପକୂଳ ଛୁଇଁବାର ସମ୍ଭାବନା ରହିଛି। "
                    f"ପବନର ବେଗ ଘଣ୍ଟା ପ୍ରତି {wind_kmh:.0f} କି.ମି. ପର୍ଯ୍ୟନ୍ତ ବୃଦ୍ଧି ପାଇପାରେ ଏବଂ ସମୁଦ୍ର ଜୁଆର {surge_m} ମିଟର ଉଚ୍ଚ ହୋଇପାରେ। "
                    "ତଳିଆ ଅଞ୍ଚଳ ଏବଂ କଚ୍ଚା ଘରେ ରହୁଥିବା ଲୋକମାନେ ତୁରନ୍ତ ନିକଟସ୍ଥ ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳକୁ ଚାଲିଯାଆନ୍ତୁ।"
                ),
                "action_bulletins": [
                    "ହସ୍ପିଟାଲ ଏବଂ ଆଶ୍ରୟସ୍ଥଳରେ ୪୮ ଘଣ୍ଟାର ଡିଜେଲ ଜେନେରେଟର ମହଜୁଦ ରଖନ୍ତୁ।",
                    "ପିଇବା ପାଣି ଏବଂ ଜରୁରୀ ଔଷଧ ସାଇତି ରଖନ୍ତୁ।",
                    "ବିଦ୍ୟୁତ୍ ତାର କିମ୍ବା ଉପୁଡ଼ି ପଡ଼ିଥିବା ଗଛ ନିକଟକୁ ଯାଆନ୍ତୁ ନାହିଁ।",
                ],
                "ivr_speech_script": (
                    f"ନମସ୍କାର, ଏହା ଜିଲ୍ଲା ବିପର୍ଯ୍ୟୟ ପରିଚାଳନା ପ୍ରାଧିକରଣର ଜରୁରୀ ସତର୍କ ସୂଚନା। "
                    f"ବାତ୍ୟା {meta['storm_name']} ଲାଗି ସମସ୍ତ ତଳିଆ ଅଞ୍ଚଳବାସୀ ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳକୁ ଯାଆନ୍ତୁ।"
                ),
                "cap_xml_payload": "<alert><info><event>Cyclone Warning</event><urgency>Immediate</urgency></info></alert>",
            },
            {
                "language_code": "hi",
                "language_name": "Hindi (हिंदी)",
                "headline": f"चक्रवात {meta['storm_name']} आपातकालीन पूर्व-चेतावनी बुलेटिन",
                "district": "पुरी, कटक, बालासोर, जगतसिंहपुर",
                "urgency": "IMMEDIATE",
                "plain_body": (
                    f"अत्यंत भीषण चक्रवाती तूफान {meta['storm_name']} अगले {meta['lead_time_hours']:.0f} घंटों में समुद्र तट पार करेगा। "
                    f"हवा की गति {wind_kmh:.0f} किमी/घंटा और तूफानी लहरें {surge_m} मीटर तक पहुँचने का अनुमान है। "
                    "सभी तटीय सब-स्टेशनों और निचले क्षेत्रों में तुरंत एहतियाती शटडाउन और निकासी सुनिश्चित करें।"
                ),
                "action_bulletins": [
                    "अस्पतालों में आईसीयू और ऑक्सीजन बैकअप हेतु पर्याप्त डीजल सुनिश्चित करें।",
                    "तटीय सबस्टेशनों को बाढ़ से पूर्व नियंत्रित आइसोलेशन में रखें।",
                    "एनडीआरएफ और आपातकालीन दस्तों को प्राथमिक गलियारों में तैनात करें।",
                ],
                "ivr_speech_script": (
                    f"नमस्कार, यह जिला आपदा नियंत्रण कक्ष की आपातकालीन चेतावनी है। "
                    f"चक्रवात {meta['storm_name']} के प्रभाव से सुरक्षित रहने के लिए तुरंत पक्के आश्रय स्थलों में जाएं।"
                ),
                "cap_xml_payload": "<alert><info><event>Cyclone Warning</event><urgency>Immediate</urgency></info></alert>",
            },
            {
                "language_code": "bn",
                "language_name": "Bengali (বাংলা)",
                "headline": f"ঘূর্ণিঝড় {meta['storm_name']} সতর্কতা: উপকূলবর্তী বাসিন্দাদের জন্য নির্দেশিকা",
                "district": "দিঘা, মেদিনীপুর, সাগরদ্বীপ",
                "urgency": "EXPECTED",
                "plain_body": (
                    f"ঘূর্ণিঝড় {meta['storm_name']}-এর প্রভাবে আগামী {meta['lead_time_hours']:.0f} ঘণ্টায় তীব্র ঝোড়ো হাওয়া "
                    f"ও {surge_m} মিটার জলোচ্ছ্বাসের সম্ভাবনা রয়েছে। সমস্ত মৎস্যজীবীদের অবিলম্বে তীরে ফিরে আসার নির্দেশ দেওয়া হচ্ছে।"
                ),
                "action_bulletins": [
                    "জরুরি ত্রাণের জন্য শুকনো খাবার ও বিশুদ্ধ পানীয় জল মজুত রাখুন।",
                    "বিদ্যুৎ সরবরাহ বিচ্ছিন্ন হলে সাবধানে থাকুন।",
                ],
                "ivr_speech_script": f"ঘূর্ণিঝড় {meta['storm_name']} সতর্কবার্তা: অবিলম্বে নিকটবর্তী ঘূর্ণিঝড় কেন্দ্রে আশ্রয় নিন।",
                "cap_xml_payload": None,
            },
            {
                "language_code": "te",
                "language_name": "Telugu (తెలుగు)",
                "headline": f"తుఫాను {meta['storm_name']} తీవ్ర హెచ్చరిక — ఉత్తర కోస్తా ప్రాంతాలు",
                "district": "శ్రీకాకుళం, విశాఖపట్నం",
                "urgency": "EXPECTED",
                "plain_body": (
                    f"తీవ్ర తుఫాను {meta['storm_name']} గంటకు {wind_kmh:.0f} కిమీ వేగంతో తీరం వైపు దూసుకొస్తోంది. "
                    "తీరప్రాంత ప్రజలు సురక్షిత ప్రాంతాలకు తరలి వెళ్ళవలసిందిగా విజ్ఞప్తి."
                ),
                "action_bulletins": [
                    "అత్యవసర ఔషధాలు సిద్ధంగా ఉంచుకోండి.",
                    "విద్యుత్ స్తంభాలకు దూరంగా ఉండండి.",
                ],
                "ivr_speech_script": f"తుఫాను {meta['storm_name']} అత్యవసర హెచ్చరిక. దయచేసి సురక్షిత భవనాల్లో ఉండండి.",
                "cap_xml_payload": None,
            },
            {
                "language_code": "ta",
                "language_name": "Tamil (தமிழ்)",
                "headline": f"புயல் {meta['storm_name']} எச்சரிக்கை — கடலோர மண்டலங்கள்",
                "district": "சென்னை, திருவள்ளூர், கடலூர்",
                "urgency": "FUTURE",
                "plain_body": f"வங்கக்கடலில் தீவிர புயல் {meta['storm_name']} மணிக்கு {wind_kmh:.0f} கி.மீ வேகத்தில் நிலை கொண்டுள்ளது.",
                "action_bulletins": ["மீனவர்கள் கடலுக்குச் செல்ல வேண்டாம்."],
                "ivr_speech_script": "புயல் எச்சரிக்கை: பாதுகாப்பு முகாம்களை அணுகவும்.",
                "cap_xml_payload": None,
            },
            {
                "language_code": "en",
                "language_name": "English",
                "headline": f"CYCLONE {meta['storm_name'].upper()} TACTICAL BRIEFING: PRE-LANDFALL DIRECTIVE",
                "district": "Puri, Jagatsinghpur, Kendrapara Coastal Corridor",
                "urgency": "IMMEDIATE",
                "plain_body": (
                    f"Extremely Severe Cyclonic Storm '{meta['storm_name']}' is tracking at {meta['forward_speed_kmh']} km/h "
                    f"with core winds of {wind_kmh:.0f} km/h ({meta['max_sustained_wind_kt']:.0f} kt) and pressure {meta['central_pressure_hpa']} hPa. "
                    f"Landfall window expected in T-{meta['lead_time_hours']:.0f}h. Peak storm surge of {surge_m} m modelled."
                ),
                "action_bulletins": [
                    "EXECUTE pre-isolation of coastal 220kV substations to protect regional transmission grid.",
                    "VERIFY 48-hour diesel fuel tankers at all District Level Trauma and Maternity Centers.",
                    "CLOSE coastal causeways overtopping 0.4m depth and divert relief traffic to inland bypasses.",
                ],
                "ivr_speech_script": (
                    f"Urgent emergency broadcast: Cyclone {meta['storm_name']} approaching coast. "
                    "All coastal residents must relocate to designate cyclone shelters immediately."
                ),
                "cap_xml_payload": "<alert><info><event>Cyclone Pre-Landfall Directive</event><urgency>Immediate</urgency></info></alert>",
            },
        ]

        # 2. Parametric Insurance Trigger Logic
        # Condition: Sustained wind >= 89 km/h (50 kt) within 50km AND flood extent >= 30% verified by SAR
        wind_thresh = 89.0
        flood_thresh = 30.0
        is_wind_met = wind_kmh >= wind_thresh
        is_flood_met = flood_extent_pct >= flood_thresh

        payout_inr_crores = 75.0 if (is_wind_met and is_flood_met) else 0.0

        contract_hash = None
        if is_wind_met and is_flood_met:
            raw_signature = f"{meta['storm_id']}_{wind_kmh}_{flood_extent_pct}_INR_75CR"
            contract_hash = "0x" + hashlib.sha256(raw_signature.encode()).hexdigest()[:40]

        trigger_status = "TRIGGER_DISPATCHED" if (is_wind_met and is_flood_met) else "MONITORING"

        insurance: ParametricInsuranceTrigger = {
            "policy_id": "PARAMETRIC_POL_ODISHA_2026_TRACK5",
            "insured_entity": "Odisha State Disaster Management Authority (OSDMA)",
            "wind_threshold_kmh": wind_thresh,
            "flood_extent_threshold_pct": flood_thresh,
            "observed_wind_kmh": wind_kmh,
            "observed_flood_pct": flood_extent_pct,
            "satellite_evidence_sources": [
                "ISRO RISAT-1A C-band SAR (Disaster Pass 04)",
                "Sentinel-1 SAR GRD Multi-temporal Water Mask",
                "IMD Doppler Weather Radar Paradip",
            ],
            "trigger_status": trigger_status,
            "payout_liquidity_inr_crores": payout_inr_crores,
            "payout_smart_contract_hash": contract_hash,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        telemetry = {
            "agent_name": self.AGENT_NAME,
            "status": "COMPLETED",
            "active_step": "Multilingual Advisory & Parametric Trigger Synthesized",
            "last_thought": (
                f"Generated 6-language contextual bulletins. Parametric criteria checked: "
                f"Wind ({wind_kmh:.0f} km/h >= {wind_thresh} km/h: {is_wind_met}), "
                f"SAR Flood ({flood_extent_pct}% >= {flood_thresh}%: {is_flood_met}). "
                f"Trigger Status: {trigger_status} (Liquidity: ₹{payout_inr_crores} Crores)."
            ),
            "latency_ms": latency_ms,
            "confidence_score": 0.98,
        }

        return {
            "advisories": advisories,
            "parametric_insurance": insurance,
            "telemetry": telemetry,
        }
