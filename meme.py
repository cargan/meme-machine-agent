import os
import requests
import json
import random
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

# --- KONFIGŪRACIJA ---
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")
OLLAMA_URL = "http://localhost:11434/api/generate"


def get_all_templates():
    """Atsisiunčia 100 populiariausių šablonų iš Imgflip API."""
    print("📡 Gaunami naujausi meme šablonai...")
    try:
        resp = requests.get("https://api.imgflip.com/get_memes").json()
        if resp.get("success"):
            # Sukuriame žodyną {pavadinimas: id}
            return {m["name"]: m["id"] for m in resp["data"]["memes"]}
    except Exception as e:
        print(f"❌ Nepavyko gauti šablonų sąrašo: {e}")
    return {}


def get_smart_meme_data(topic, all_templates):
    """AI parenka šabloną iš sąrašo ir sugalvoja tekstą."""
    # Kad AI nepasimestų, duodame jam 25 atsitiktinius šablonus iš 100-uko
    template_names = list(all_templates.keys())
    sampled_templates = random.sample(template_names, min(25, len(template_names)))

    prompt = f"""
    You are a meme expert.
    Topic: {topic}
    Available templates: {sampled_templates}

    Task:
    1. Pick the best template from the list above.
    2. Create funny top and bottom text.
    3. Return ONLY a JSON object.

    JSON Structure:
    {{
        "template_name": "exact_name_from_list",
        "top": "text",
        "bottom": "text"
    }}
    """

    payload = {"model": "llama3", "prompt": prompt, "stream": False, "format": "json"}

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_res = response.json().get("response", "{}")
        return json.loads(raw_res)
    except Exception as e:
        print(f"❌ AI klaida: {e}")
        return None


def download_meme(url, topic):
    """Išsaugo sugeneruotą meme į 'memes' aplanką."""
    if not os.path.exists("memes"):
        os.makedirs("memes")

    safe_topic = topic.replace(" ", "_")[:15]
    filename = f"memes/{safe_topic}_{datetime.now().strftime('%H%M%S')}.jpg"

    try:
        img_data = requests.get(url).content
        with open(filename, "wb") as f:
            f.write(img_data)
        return filename
    except Exception as e:
        print(f"❌ Nepavyko atsisiųsti: {e}")
        return None


def generate_meme(topic, all_templates):
    """Sujungia visus žingsnius į vieną procesą."""
    ai_data = get_smart_meme_data(topic, all_templates)

    if not ai_data or "template_name" not in ai_data:
        print("❌ AI nesugebėjo suformuoti atsakymo. Bandykite kitą temą.")
        return

    t_name = ai_data["template_name"]

    if t_name not in all_templates:
        print(f"❌ AI parinktas šablonas '{t_name}' nerastas sąraše. Bandom Drake...")
        t_id = "181913649"  # Drake ID kaip atsarginis
    else:
        t_id = all_templates[t_name]
        print(f"✅ Parinktas šablonas: {t_name}")

    # Siuntimas į Imgflip
    payload = {
        "template_id": t_id,
        "username": IMGFLIP_USERNAME,
        "password": IMGFLIP_PASSWORD,
        "text0": ai_data.get("top", ""),
        "text1": ai_data.get("bottom", ""),
    }

    try:
        resp = requests.post(
            "https://api.imgflip.com/caption_image", data=payload
        ).json()
        if resp.get("success"):
            url = resp["data"]["url"]
            path = download_meme(url, topic)
            print(f"🎉 Sukurta! {path}")
            print(f"🔗 Nuoroda: {url}")
        else:
            print(f"❌ Imgflip API klaida: {resp.get('error_message')}")
    except Exception as e:
        print(f"❌ Ryšio klaida: {e}")


# --- PAGRINDINIS CIKLAS ---
def main():
    # Pirmiausia gauname visus įmanomus šablonus
    all_templates = get_all_templates()

    if not all_templates:
        print("❌ Nepavyko užkrauti šablonų. Patikrinkite interneto ryšį.")
        return

    print(f"✅ Sėkmingai užkrauta {len(all_templates)} šablonų.")

    while True:
        topic = input("\n💡 Įvesk meme temą (arba 'q' išeiti): ")
        if topic.lower() == "q":
            print("Iki kito karto! 👋")
            break

        generate_meme(topic, all_templates)


if __name__ == "__main__":
    main()
