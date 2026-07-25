import base64
import logging
import os

import requests
import trafilatura
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

load_dotenv()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # "Rachel", a default premade voice
MODEL_ID = "eleven_multilingual_v2"
MAX_CHARS = 2500  # caps the request to save API credits

app = Flask(__name__, static_folder=".", static_url_path="")
log = logging.getLogger("article-to-audio")

ERROR_MESSAGES = {
    "quota_exceeded": "API quota exceeded — credits reset monthly.",
    "invalid_api_key": "That ElevenLabs API key isn't valid — check your .env file.",
    "missing_permissions": "Your ElevenLabs API key doesn't have permission to generate speech.",
    "too_many_concurrent_requests": "Too many requests at once — wait a moment and try again.",
    "voice_not_found": "Couldn't find the configured voice — check ELEVENLABS_VOICE_ID in .env.",
}


def humanize_elevenlabs_error(status_code, body_json):
    detail = body_json.get("detail") if isinstance(body_json, dict) else None
    status = detail.get("status") if isinstance(detail, dict) else detail if isinstance(detail, str) else None

    if status in ERROR_MESSAGES:
        return ERROR_MESSAGES[status]
    if status_code == 401:
        return ERROR_MESSAGES["invalid_api_key"]
    if status_code == 404:
        return ERROR_MESSAGES["voice_not_found"]
    if status_code == 429:
        return ERROR_MESSAGES["quota_exceeded"]
    return "Something went wrong generating the audio. Please try again."


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
        return jsonify(error="That doesn't look like a valid URL — it should start with http:// or https://"), 400

    try:
        downloaded = trafilatura.fetch_url(url)
    except Exception:
        downloaded = None
    if not downloaded:
        return jsonify(error="Couldn't read that page — try a different article link."), 400

    try:
        text = trafilatura.extract(downloaded, favor_recall=True)
        title = trafilatura.extract_metadata(downloaded).title
    except Exception:
        text, title = None, None

    if not text or len(text.strip()) < 40:
        return jsonify(error="Couldn't find readable article text on that page — try a different link."), 400

    full_char_count = len(text)
    text = text[:MAX_CHARS]
    used_char_count = len(text)

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
        return jsonify(error="Couldn't reach the ElevenLabs API — check your connection and try again."), 502

    if eleven_response.status_code != 200:
        body_json = None
        try:
            body_json = eleven_response.json()
        except ValueError:
            pass
        log.warning("ElevenLabs error %s: %s", eleven_response.status_code, eleven_response.text[:500])
        return jsonify(error=humanize_elevenlabs_error(eleven_response.status_code, body_json)), 502

    return jsonify(
        title=title or "Untitled article",
        fullCharCount=full_char_count,
        usedCharCount=used_char_count,
        truncated=full_char_count > MAX_CHARS,
        audioBase64=base64.b64encode(eleven_response.content).decode("ascii"),
    )


@app.errorhandler(Exception)
def handle_unexpected_error(err):
    if isinstance(err, HTTPException):
        return err
    log.exception("Unexpected error")
    return jsonify(error="Something unexpected went wrong. Please try again."), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="127.0.0.1", port=port, debug=True)
