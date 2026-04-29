import argparse
import os
import requests
import json
import random
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

AUTO_TOPICS = [
    "Programming in Neovim",
    "AI agents taking over the world",
    "Fish in a 112L aquarium",
    "LRT Opus radio vibes",
    "Debugging at 3 AM"
]

# config
# variables defined in .env file
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

# ollama local
# https://ollama.com/
# OLLAMA_URL = "http://localhost:11434/api/generate"
# Cloud/Github Actions
GROQ_API_KEY = os.getenv('GROQ_API_KEY')


def get_all_templates():
    print("📡 Getting newest meme templates...")
    try:
        resp = requests.get("https://api.imgflip.com/get_memes").json()
        if resp.get("success"):
            return {m["name"]: m["id"] for m in resp["data"]["memes"]}
    except Exception as e:
        print(f"❌ Could not fetch templates: {e}")
    return {}

def get_smart_meme_data(topic, all_templates):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Maksimaliai sumažiname šablonų kiekį iki 8, kad AI nepasimestų
    template_names = list(all_templates.keys())
    sampled = random.sample(template_names, min(8, len(template_names)))

    # Labai paprastas ir aiškus nurodymas
    prompt = f"""
    Topic: {topic}
    Templates: {sampled}
    Task: Pick one template and write top/bottom captions.
    Output: Return ONLY a JSON object.
    Example: {{"template_name": "{sampled[0]}", "top": "text", "bottom": "text"}}
    """

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a JSON-only response bot."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1, # Beveik nulinis kūrybiškumas struktūrai užtikrinti
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"❌ Groq API Klaida! Statusas: {response.status_code}")
            print(f"❌ Detalės: {response.text}")
            return None

        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"❌ Kritinė klaida: {e}")
        return None

# OLLAMA
# def get_smart_meme_data(topic, all_templates):
#     template_names = list(all_templates.keys())
#     sampled_templates = random.sample(template_names, min(25, len(template_names)))
#
#     prompt = f"""
#     You are a meme expert.
#     Topic: {topic}
#     Available templates: {sampled_templates}
#
#     Task:
#     1. Pick the best template from the list above.
#     2. Create funny top and bottom text.
#     3. Return ONLY a JSON object.
#
#     JSON Structure:
#     {{
#         "template_name": "exact_name_from_list",
#         "top": "text",
#         "bottom": "text"
#     }}
#     """
#
#     payload = {"model": "llama3", "prompt": prompt, "stream": False, "format": "json"}
#
#     try:
#         response = requests.post(OLLAMA_URL, json=payload)
#         response.raise_for_status()
#         raw_res = response.json().get("response", "{}")
#         return json.loads(raw_res)
#     except Exception as e:
#         print(f"❌ AI klaida: {e}")
#         return None
#

def download_meme(url, topic):
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
        print(f"❌ Error saving: {e}")
        return None


def generate_meme_groq(topic, all_templates):
    ai_data = get_smart_meme_data(topic, all_templates)
    if not ai_data or "template_name" not in ai_data:
        print("❌ AI failed to generate response.")
        return

    t_name = ai_data["template_name"]

    if t_name not in all_templates:
        print(f"❌ AI template selected '{t_name}' not found. Fallback to default...")
        t_id = "181913649"  # Drake ID default
    else:
        t_id = all_templates[t_name]
        print(f"✅ Meme template: {t_name}")

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
            print(f"🎉 Created! {path}")
            print(f"🔗 URL: {url}")
        else:
            print(f"❌ Imgflip API error: {resp.get('error_message')}")
    except Exception as e:
        print(f"❌ Error communicating: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Run in automatic mode")
    args = parser.parse_args()

    all_templates = get_all_templates()

    if args.auto:
        topic = random.choice(AUTO_TOPICS)
        print(f"🤖 Automatinis režimas. Tema: {topic}")
    else:
        topic = input("Įvesk temą: ")

    # generate_meme_ollama(topic, all_templates)
    generate_meme_groq(topic, all_templates)
    # all_templates = get_all_templates()
    #
    # if not all_templates:
    #     print("❌ Error loading templates")
    #     return
    #
    # print(f"✅ Templates loaded #{len(all_templates)} .")
    #
    # while True:
    #     topic = input("\n💡 Input meme idea ('q' to quit): ")
    #     if topic.lower() == "q":
    #         print("Bye! 👋")
    #         break
    #
    #     generate_meme(topic, all_templates)


if __name__ == "__main__":
    main()
