# Article to Audio

<!-- Demo GIF placeholder — record a ~15s screen capture of pasting a URL through to playing/downloading the audio, then drop it here:
![Article to Audio demo](./demo.gif)
-->

Paste a link to any article, and get back a playable, downloadable narration of it — powered by the [ElevenLabs](https://elevenlabs.io) text-to-speech API.

## How it works

1. You paste an article URL into the single-page frontend.
2. A small backend server fetches the page and extracts just the readable article text (stripping nav, ads, comments, etc.).
3. The backend sends that text to the ElevenLabs API server-side, so your API key never touches the browser.
4. The resulting audio is returned to the page as a playable `<audio>` player with a download button.

## Setup

**Requirements:** Python 3.10+

```bash
# 1. Clone and enter the project
git clone git@github.com:daniellaseberini/article-to-audio.git
cd article-to-audio

# 2. Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Add your ElevenLabs API key
cp .env.example .env
# then open .env and paste in your key from https://elevenlabs.io/app/settings/api-keys

# 4. Run it
python3 server.py
```

Then open `http://localhost:5050`.

## Tech stack

- **Backend:** Python + Flask — the only part that talks to the ElevenLabs API, using a key loaded from `.env` (never sent to or stored in the browser)
- **Article extraction:** [trafilatura](https://trafilatura.readthedocs.io/), for pulling clean readable text out of arbitrary article pages
- **Frontend:** a single static HTML page, vanilla JS, no framework or build step
- **Text-to-speech:** [ElevenLabs API](https://elevenlabs.io/docs/api-reference/text-to-speech)

## Notes / limitations

- Articles are truncated to the first 5,000 characters per conversion, to stay within typical ElevenLabs per-request limits
- Uses a single default voice (ElevenLabs' premade "Rachel"); override it by setting `ELEVENLABS_VOICE_ID` in `.env`
- No accounts, database, or history — every conversion is a fresh, one-off request

## Future ideas

(Deliberately not built, to keep this a small tool that works well rather than a big one that's half-broken.)

- Voice picker in the UI instead of a fixed default
- Chunk long articles into multiple TTS requests and stitch the audio together, instead of truncating
- Conversion history / a library of past narrations
- Support for pasting raw text directly, not just URLs
