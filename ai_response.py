import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NEBIUS_API_KEY", "fallback_secret")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}


def ai_response(name, genre, plot, target_audience, writing_style, prev_story, choice):
    prev = prev_story if prev_story else "There's no previous story, so start fresh."

    system_prompt = (
        f"You are an AI model that generates an incomplete (~100 words) single paragraph story "
        f"with user's name '{name}' as a character. "
        f"Genre: '{genre}', Target audience: '{target_audience}', Style: '{writing_style}'. "
        f"If previous paragraph is given, continue it while integrating the user's last choice '{choice}'. "
        f"If not, start fresh. STRICT FORMAT RULES: "
        f"1. Start with a 5-word scene description & "
        f"2. Then the story paragraph & "
        f"3. [Choice 1] & [Choice 2] with '&' between. "
        f"NO extra text. Final output format: "
        f"[Scene description] & [Story paragraph] & [Choice 1] & [Choice 2]. "
        f"Plot: {plot}. Previous paragraph: {prev}."
    )

    payload = {
        "model": "Qwen/Qwen3-30B-A3B",
        "messages": [
            {"role": "system", "content": system_prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://api.studio.nebius.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()

        # ✅ Clean AI's thinking text if present
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()

        parts = [p.strip() for p in content.split("&") if p.strip()]

        if len(parts) != 4:
            raise ValueError(f"AI response format invalid. Got: {content}")

        return parts[0], parts[1], parts[2], parts[3]

    except Exception as e:
        print(f"[AI ERROR] {e}")
        return "Error", "AI response failed.", "Try Again", "Try Again"

def generate_image(prompt):
    image_payload = {
        "model": "black-forest-labs/flux-schnell",
        "prompt": prompt,
        "response_format": "url",
        "extra_body": {
            "response_extension": "webp",
            "width": 512,
            "height": 512,
            "num_inference_steps": 16,
            "seed": -1,
            "negative_prompt": "giraffes, night sky"
        }
    }

    try:
        response = requests.post(
            "https://api.studio.nebius.com/v1/images/generations",
            headers=headers,
            json=image_payload
        )
        response.raise_for_status()
        result = response.json()
        return result["data"][0]["url"] if result["data"] else "https://dummyimage.com/512x512/000/fff&text=No+Image"
    except Exception as e:
        print(f"[IMAGE ERROR] {e}")
        return "https://dummyimage.com/512x512/000/fff&text=No+Image"
