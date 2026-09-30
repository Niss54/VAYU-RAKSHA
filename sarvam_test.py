import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

api_key = os.getenv("SARVAM_API_KEY")

if not api_key or api_key.startswith("["):
    print("ERROR: SARVAM_API_KEY not set in .env", file=sys.stderr)
    sys.exit(1)

from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key=api_key)

response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[
        {
            "role": "user",
            "content": "Namaste! You are VAYU-RAKSHA. Give a 1-sentence emergency warning for coastal Odisha in Hindi and English.",
        }
    ],
)

print("\n=== SARVAM AI (sarvam-105b-conversations) OUTPUT ===")
print(response.choices[0].message.content)
print("===================================================\n")
