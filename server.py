import base64
import os

import requests
import trafilatura
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # "Rachel", a default premade voice
MODEL_ID = "eleven_multilingual_v2"
MAX_CHARS = 5000  # keeps a single request within typical ElevenLabs per-request limits

app = Flask(__name__, static_folder=".", static_url_path="")


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.post("/api/convert")
def convert():
    if not ELEVENLABS_API_KEY:
        return jsonify(error="Server is missing ELEVENLABS_API_KEY. Add it to your .env file and restart the server."), 500

    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        return jsonify(error="Please enter a valid article URL, starting with http:// or https://"), 400

    try:
        downloaded = trafilatura.fetch_url(url)
    except Exception:
        downloaded = None
    if not downloaded:
        return jsonify(error="Couldn't fetch that URL. Check the link and try again."), 400

    text = trafilatura.extract(downloaded, favor_recall=True)
    title = trafilatura.extract_metadata(downloaded).title if downloaded else None

    if not text or len(text.strip()) < 40:
        return jsonify(error="Couldn't find readable article text on that page."), 400

    truncated = len(text) > MAX_CHARS
    text = text[:MAX_CHARS]

    try:
        eleven_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json={
                "text": text,
                "model_id": MODEL_ID,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
            timeout=120,
        )
    except requests.RequestException:
        return jsonify(error="Couldn't reach the ElevenLabs API. Please try again."), 502

    if eleven_response.status_code != 200:
        message = eleven_response.text[:300]
        return jsonify(error=f"ElevenLabs API error ({eleven_response.status_code}): {message}"), 502

    return jsonify(
        title=title or "Untitled article",
        truncated=truncated,
        charCount=len(text),
        audioBase64=base64.b64encode(eleven_response.content).decode("ascii"),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="127.0.0.1", port=port, debug=True)
