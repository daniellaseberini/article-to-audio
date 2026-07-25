# Article to Audio

<!-- Demo GIF placeholder — record a ~15s screen capture showing: the demo-mode "Try a sample article" card, clicking it, the sped-up "Fetching → Extracting → Generating" pipeline animating through, and the result card with the player. Editorial paper-tone design with Fraunces/Archivo type — the GIF should show that off. Drop it here:
![Article to Audio demo](./demo.gif)
-->

**[Live demo →](https://article-to-audio-daniellaseberini-4420s-projects.vercel.app)** (runs in demo mode — see below)

Paste a link to any article, and get back a playable, downloadable narration of it — powered by the [ElevenLabs](https://elevenlabs.io) text-to-speech API.

## How it works

1. You paste an article URL into the single-page frontend.
2. A small backend server fetches the page and extracts just the readable article text (stripping nav, ads, comments, etc.).
3. The backend sends that text to the ElevenLabs API server-side, so your API key never touches the browser.
4. The resulting audio is returned to the page as a playable `<audio>` player with a download button.

## Demo mode

The public deployment doesn't call the ElevenLabs API at all — it has no key, and no backend is even deployed. Instead, the frontend detects it isn't running on `localhost` and switches to demo mode: the URL input is replaced with a "Try a sample article" card that plays a pre-generated narration stored in the repo under `demo-audio/`, using the same pipeline animation and result UI (sped up, since there's no real work happening).

The sample list lives in `demo-audio/samples.json` — each entry has a `title`, `source`, a `clipFile` (played inline) and a `fullFile` (what the download button serves; can be a longer version of the same narration). Add more entries to show more sample cards.

Running the app locally with a valid `ELEVENLABS_API_KEY` in `.env` always gives you the full live experience — mode detection is automatic and based purely on hostname, not a manual flag.

**Current status:** the one sample in the repo right now is a placeholder narrated with the local macOS `say` command, not ElevenLabs — clearly labeled as such in the UI. It's there so the demo isn't empty while API credits are unavailable; swap in a real ElevenLabs narration by replacing the file and updating `samples.json` whenever credits allow.

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
- **Frontend:** a single static HTML page, vanilla JS, no framework or build step — editorial/print-inspired design set in [Fraunces](https://fonts.google.com/specimen/Fraunces) (display serif) and [Archivo](https://fonts.google.com/specimen/Archivo) (UI/body)
- **Text-to-speech:** [ElevenLabs API](https://elevenlabs.io/docs/api-reference/text-to-speech)

## Notes / limitations

- Articles are capped at the first 2,500 characters per conversion to save API credits — this is shown transparently in the UI after extraction (e.g. "Article: 8,400 characters — converting the first 2,500 to save API credits")
- ElevenLabs errors (quota exceeded, invalid key, etc.) are caught server-side and translated into plain-language messages in the UI, instead of raw API responses
- Uses a single default voice (ElevenLabs' premade "Rachel"); override it by setting `ELEVENLABS_VOICE_ID` in `.env` — some accounts may need to set this, since voice availability varies by account
- No accounts, database, or history — every conversion is a fresh, one-off request

## Future ideas

(Deliberately not built, to keep this a small tool that works well rather than a big one that's half-broken.)

- Voice picker in the UI instead of a fixed default
- Chunk long articles into multiple TTS requests and stitch the audio together, instead of truncating
- Conversion history / a library of past narrations
- Support for pasting raw text directly, not just URLs
