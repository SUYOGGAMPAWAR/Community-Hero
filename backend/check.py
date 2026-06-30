from google import genai
import sys

print("\n--- MODEL CHECKER ---")
key = input("Paste your BRAND NEW API key here and press Enter: ").strip()

if key.startswith("AIzaSyB0dyc1"):
    print("\n❌ STOP: You pasted the old leaked key! You must go to AI Studio and generate a new one.")
    sys.exit(1)

try:
    client = genai.Client(api_key=key)
    print("\n✅ Key accepted! Fetching your allowed models...\n")
    for m in client.models.list():
        if "vision" in m.name or "flash" in m.name or "pro" in m.name:
            print(m.name)
except Exception as e:
    print("\n❌ ERROR:", e)
