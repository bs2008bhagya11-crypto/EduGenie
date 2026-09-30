# EduGenie Advanced — Gemini Flash

EduGenie is an AI-powered learning assistant built with **FastAPI + Google Gemini Flash**.

## What's changed in this advanced version?

- All AI features use the same Gemini Flash pipeline.
- Removed the local LaMini-Flan-T5 model.
- Removed `torch`, `transformers`, and `sentencepiece`.
- Default model: `gemini-3.8-flash`.
- Added conversational `/chat` endpoint.
- Added configurable quiz size: 5, 7, or 10 questions.
- Added summary modes: quick revision, detailed, and exam notes.
- Added a redesigned responsive web UI.
- Added stronger prompts for tutoring, assessments, summaries, and roadmaps.
- Added health information showing the active Gemini model.
- Added automated API tests.

Google's current Gemini API model documentation lists Gemini 3.8 Flash as a stable Flash model and recommends current Flash models for new projects.

## Folder structure

```text
EduGenie/
├── main.py
├── config.py
├── schemas.py
├── gemini_client.py
├── qna.py
├── explanation_module.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── tests/
    └── test_api.py
```

## 1. Install Python

Use Python 3.10+.

Check:

```powershell
python --version
```

## 2. Open the project in VS Code

Extract the ZIP and open the `EduGenie` folder in VS Code.

## 3. Create virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Create `.env`

Copy `.env.example` to `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then open `.env` and set:

```env
GEMINI_API_KEY=YOUR_GOOGLE_AI_STUDIO_KEY
GEMINI_MODEL=gemini-3.8-flash
```

Never put the API key inside `app.js`, `index.html`, or any frontend file.

## 6. Run

```powershell
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 7. Test

```powershell
pytest -q
```

The tests mock Gemini calls, so they do not require API quota.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web application |
| GET | `/health` | App + Gemini status |
| POST | `/qa` | AI question answering |
| POST | `/explain` | Deep concept explanation |
| POST | `/quiz` | 3-10 MCQ generation |
| POST | `/summarize` | Quick/detailed/exam summary |
| POST | `/learn/recommendations` | Personalized learning roadmap |
| POST | `/chat` | Contextual AI tutor conversation |

## Important

If you previously had:

```env
GEMINI_MODEL=gemini-3.8-flash
```

keep it.

If your Google account does not expose that model, choose a currently available Flash model in Google AI Studio and change only `GEMINI_MODEL`.

Do not install the old local-model packages from the previous project. This version intentionally uses Gemini Flash for every AI feature.

## Troubleshooting

### `Gemini API is not configured`

Check `.env`:

```env
GEMINI_API_KEY=your_real_key
```

Then restart Uvicorn.

### `Gemini request failed`

Check:
- API key is valid.
- The selected model is available to your Google AI account.
- Internet access is working.
- You have not exceeded the API quota.

### Server keeps loading

Stop the server with `CTRL+C`, then run:

```powershell
uvicorn main:app --reload
```

If port 8000 is busy:

```powershell
uvicorn main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```
