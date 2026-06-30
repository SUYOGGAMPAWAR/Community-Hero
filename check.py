from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

print("Your allowed models are:")
for m in client.models.list():
    print(m.name)
