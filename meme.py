import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


# Konfigūracija iš aplinkos kintamųjų
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")
OLLAMA_URL = "http://localhost:11434/api/generate"


def get_meme_text_from_ai(topic):
    """Naudoja Ollama sugeneruoti meme tekstą."""
    prompt = f"""
    Create a funny meme for the 'Drake Hotline Bling' format about the topic: {topic}.
    The format needs two parts:
    1. Something Drake REJECTS (Top text)
    2. Something Drake APPROVES (Bottom text)

    Respond ONLY with a JSON object like this:
    {{"top": "text here", "bottom": "text here"}}
    """

    payload = {
        "model": "llama3",  # Arba tavo naudojamas modelis
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return json.loads(result["response"])
    except Exception as e:
        print(f"❌ Klaida su Ollama: {e}")
        return None


def create_meme_imgflip(top_text, bottom_text):
    """Išsiunčia tekstą į Imgflip API ir gauna sugeneruoto meme URL."""
    url = "https://api.imgflip.com/caption_image"

    # Drake Hotline Bling šablono ID yra 181913649
    data = {
        "template_id": "181913649",
        "username": IMGFLIP_USERNAME,
        "password": IMGFLIP_PASSWORD,
        "text0": top_text,
        "text1": bottom_text,
    }

    try:
        response = requests.post(url, data=data)
        result = response.json()
        if result["success"]:
            return result["data"]["url"]
        else:
            print(f"❌ Imgflip klaida: {result['error_message']}")
            return None
    except Exception as e:
        print(f"❌ Klaida jungiantis prie Imgflip: {e}")
        return None


def main():
    topic = input("Įveskite temą meme'ui (pvz. 'Python programming'): ")

    print("🧠 AI galvoja juokelį...")
    texts = get_meme_text_from_ai(topic)

    if texts:
        print(f"✅ AI sugalvojo:\nTop: {texts['top']}\nBottom: {texts['bottom']}")
        print("🖼️ Generuojamas paveiksliukas...")

        meme_url = create_meme_imgflip(texts["top"], texts["bottom"])

        if meme_url:
            print(f"\n🎉 Tavo meme paruoštas! Peržiūrėk čia:\n{meme_url}")
        else:
            print("Nepavyko sugeneruoti paveiksliuko.")


if __name__ == "__main__":
    main()
