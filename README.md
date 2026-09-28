# SpeechTranscription_Hindi

Batch-transcribe Hindi audio clips (`.mpeg`, `.mp3`, `.wav`) to text using the [Sarvam AI](https://docs.sarvam.ai) Speech-to-Text Batch API (Saaras).

Built to turn recorded scene dialogue into text for a children's Janmashtami play, but works for any Hindi (or other Indic language) audio.

## Features

- Transcribes every audio file in `clips/` in a single batch job
- Handles clips longer than 30 seconds (Batch API supports up to 2 hours per file)
- Keeps output in Devanagari script (`mode="transcribe"`)
- API key loaded from a `.env` file, never hardcoded

## Prerequisites

- Python 3.9+
- A Sarvam AI API key from [dashboard.sarvam.ai](https://dashboard.sarvam.ai/)

## Project structure

```
SpeechTranscription_Hindi/
├── clips/              # put your audio files here
├── transcripts/        # output JSON files are written here
├── .env                # SARVAM_API_KEY=your_key_here (not committed)
├── .gitignore
├── requirements.txt
├── transcribe.py
└── README.md
```

## Setup

### 1. Clone and create a virtual environment

**Windows (PowerShell)**
```powershell
git clone https://github.com/<your-username>/SpeechTranscription_Hindi.git
cd SpeechTranscription_Hindi
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
git clone https://github.com/<your-username>/SpeechTranscription_Hindi.git
cd SpeechTranscription_Hindi
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -U pip -r requirements.txt
```

`requirements.txt`:
```
sarvamai
python-dotenv
```

> Use `python -m pip` rather than bare `pip` so packages install into the active venv and not your global Python.

### 3. Configure your API key

Create a `.env` file in the project root:

```
SARVAM_API_KEY=your_actual_key_here
```

No quotes, no spaces around `=`. Make sure the file is named `.env` and not `.env.txt` (Windows Explorer hides extensions by default).

## Usage

1. Copy your audio files into `clips/`
2. Run:

```bash
python transcribe.py
```

3. Transcripts appear in `transcripts/`, one JSON file per clip (e.g. `Scene1.mpeg.json`).

### `transcribe.py`

```python
import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

audio_dir = "clips"
output_dir = "transcripts"
os.makedirs(output_dir, exist_ok=True)

files = [
    os.path.join(audio_dir, f)
    for f in os.listdir(audio_dir)
    if f.lower().endswith((".wav", ".mp3", ".mpeg"))
]

if not files:
    print("No audio files found in clips/")
else:
    job = client.speech_to_text_job.create_job(
        model="saaras:v3",
        mode="transcribe",       # "translate" for English, "translit" for romanized
        language_code="hi-IN",
    )
    job.upload_files(file_paths=files)
    job.start()
    print("Job started, waiting for completion...")
    job.wait_until_complete()
    job.download_outputs(output_dir=output_dir)
    print(f"Done. Transcripts saved in {output_dir}/")
```

## Output format

Each output file looks like this:

```json
{
  "request_id": "...",
  "transcript": "नहीं, मेरा बच्चा। ...",
  "language_code": "hi-IN",
  "timestamps": null,
  "diarized_transcript": null
}
```

The text you want is in the `transcript` field. To extract plain `.txt` files:

```python
import json, glob, os

for path in glob.glob("transcripts/*.json"):
    with open(path, encoding="utf-8") as f:
        text = json.load(f)["transcript"]
    with open(os.path.splitext(path)[0] + ".txt", "w", encoding="utf-8") as out:
        out.write(text)
```

## Modes

| `mode` | Output |
|---|---|
| `transcribe` | Hindi text in Devanagari (default in this project) |
| `translate` | English translation |
| `translit` | Hindi romanized in Latin script |
| `verbatim` | Word-for-word, including fillers |
| `codemix` | Mixed Hindi-English output |

## Notes and limitations

- **REST vs Batch:** Sarvam's synchronous REST endpoint rejects audio over 30 seconds. This project uses the Batch API to avoid that limit.
- **Empty transcripts:** clips with no speech (silence, music, sound effects) return `"transcript": ""` and `language_code: null`. That is expected, not an error.
- **Accuracy:** proper nouns, mythological names, and heavily dramatized or overlapping speech may need manual review. Always proofread before using the text.
- **`.mpeg` on Windows:** if you switch to the synchronous REST endpoint, Windows maps `.mpeg` to `video/mpeg` and Sarvam rejects it. Pass the file as a tuple with an explicit type: `file=(fname, f, "audio/mpeg")`, or rename to `.mp3`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python3` not found on Windows | Use `python`; disable the Microsoft Store aliases under Settings > Apps > Advanced app settings > App execution aliases |
| `ModuleNotFoundError: dotenv` | Run `python -m pip install -r requirements.txt` with the venv active |
| Packages install to global Python | Use `python -m pip`, not `pip`; verify with `python -c "import sys; print(sys.prefix)"` |
| `KeyError: 'SARVAM_API_KEY'` | Check `.env` exists in the project root and is not named `.env.txt` |
| Activation script blocked | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` |

## Recommended `.gitignore`

```
.env
venv/
__pycache__/
clips/
transcripts/
```

## License

Add a license of your choice (e.g. MIT) before publishing.

## Acknowledgements

- [Sarvam AI](https://www.sarvam.ai) for the Saaras speech-to-text models
