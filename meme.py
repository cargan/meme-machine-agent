import os
import requests
import json
import random
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

# config
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")
# ollama local
OLLAMA_URL = "http://localhost:11434/api/generate"


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


def generate_meme(topic, all_templates):
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
    all_templates = get_all_templates()

    if not all_templates:
        print("❌ Error loading templates")
        return

    print(f"✅ Templates loaded #{len(all_templates)} .")

    while True:
        topic = input("\n💡 Input meme idea ('q' to quit): ")
        if topic.lower() == "q":
            print("Bye! 👋")
            break

        generate_meme(topic, all_templates)


if __name__ == "__main__":
    main()
