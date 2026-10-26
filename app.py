import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def ask_gemini(prompt: str):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None, "server is not configured yet (GEMINI_API_KEY missing)"
    try:
        r = requests.post(
            GEMINI_URL,
            params={"key": key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=45,
        )
    except requests.RequestException:
        return None, "could not reach the ai service"
    if r.status_code != 200:
        return None, f"ai request failed ({r.status_code})"
    try:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"], None
    except (KeyError, IndexError, ValueError):
        return None, "could not read the ai answer"


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/api/check", methods=["POST"])
def check():
    data = request.get_json(silent=True) or {}
    business = (data.get("business") or "").strip()
    city = (data.get("city") or "").strip()
    language = (data.get("language") or "english").strip()
    if not business or not city:
        return jsonify({"error": "business name and city are required"}), 400

    prompt = (
        f"Answer in {language}. You are auditing how visible a business is inside AI answers.\n"
        f'Step 1: identify what kind of business "{business}" is (one short phrase).\n'
        f'Step 2: answer the question a customer would ask an AI assistant: '
        f'"best <that kind of business> in {city}" — list the businesses you would name.\n'
        f"Output exactly this format:\n"
        f"TYPE: <one short phrase>\n"
        f"LIST:\n"
        f"1. <name>\n2. <name>\n3. <name>\n4. <name>\n5. <name>\n"
        f"6. <name>\n7. <name>\n8. <name>\n9. <name>\n10. <name>"
    )
    answer, err = ask_gemini(prompt)
    if err:
        return jsonify({"error": err}), 502

    type_phrase = ""
    names = []
    for line in answer.splitlines():
        s = line.strip()
        if s.upper().startswith("TYPE:"):
            type_phrase = s[5:].strip()
        elif len(s) > 2 and s[0].isdigit() and "." in s[:4]:
            names.append(s.split(".", 1)[1].strip())

    return jsonify({
        "business": business,
        "city": city,
        "language": language,
        "type": type_phrase,
        "named": business.lower() in answer.lower(),
        "competitors": names[:10],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
