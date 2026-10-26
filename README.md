# AI Visibility Checker (MVP)

Free check: a business owner types their business name + city (any language) and
sees whether an AI assistant (Gemini, queried the way customers ask ChatGPT)
names their business or their competitors when asked for "best X in city".

## Stack
- Flask app (app.py) + single landing page (static/index.html)
- Gemini via the Google Generative Language REST API, key read from GEMINI_API_KEY
- Deploys free on Render (render.yaml included)

## Deploy on Render (free tier)
1. Push this repo to GitHub.
2. Render > New > Blueprint, pick the repo (render.yaml sets the service).
3. Add env var GEMINI_API_KEY with a Google AI Studio key.
4. Deploy. Share the URL with small businesses.

## Local run
```
pip install -r requirements.txt
GEMINI_API_KEY=yourkey python app.py
```
