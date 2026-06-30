"""
MoodMate – Flask REST API (skeleton)
-------------------------------------
This mirrors the mock logic used in the frontend prototype so the two stay
in sync. Swap the mock functions below for real models (scikit-learn /
TensorFlow / OpenCV) without changing the route contracts the frontend
expects.

Run:
    pip install flask flask-cors --break-system-packages
    python flask_backend.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import re

app = Flask(__name__)
CORS(app) 

@app.route("/")
def home():
    return send_file("moodmate.html")

CORS(app)  # allow the React/HTML frontend to call this during development

# ---------------------------------------------------------------------------
# Mock "model" — keyword lexicon, same logic as analyzeText() in the frontend.
# Replace with a trained classifier (e.g. TF-IDF + LogisticRegression, or a
# fine-tuned transformer) behind the same predict_emotion() signature.
# ---------------------------------------------------------------------------
LEXICON = {
    "Happy":   ["happy", "great", "good", "glad", "joy", "excited", "awesome", "love", "grateful", "smile"],
    "Calm":    ["calm", "relaxed", "peaceful", "fine", "okay", "steady", "content", "chill"],
    "Sad":     ["sad", "down", "low", "upset", "cry", "crying", "hurt", "depressed", "blue"],
    "Angry":   ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "rage"],
    "Stress":  ["stressed", "stress", "overwhelmed", "deadline", "pressure", "busy", "exhausted"],
    "Anxious": ["anxious", "anxiety", "worried", "nervous", "panic", "scared", "afraid"],
    "Lonely":  ["lonely", "alone", "isolated", "empty", "disconnected"],
    "Excited": ["excited", "thrilled", "pumped", "stoked"],
    "Fear":    ["fear", "afraid", "terrified", "frightened"],
    "Neutral": ["fine", "okay", "normal", "usual"],
}

RECOMMENDATIONS = {
    "Happy":   [{"icon": "🎉", "title": "Celebration Playlist", "desc": "Keep the energy going"},
                {"icon": "✅", "title": "Productivity Sprint", "desc": "Channel it into a task you've put off"}],
    "Calm":    [{"icon": "📖", "title": "Mindful Reading", "desc": "15 pages of something light"},
                {"icon": "🚶", "title": "Gentle Walk", "desc": "Stay in this steady state"}],
    "Sad":     [{"icon": "💬", "title": "Motivational Quotes", "desc": "A short reset for your mindset"},
                {"icon": "🎵", "title": "Relaxing Music", "desc": "Soft instrumentals, 20 min"}],
    "Angry":   [{"icon": "🌬️", "title": "Box Breathing", "desc": "4 counts in, 4 hold, 4 out"},
                {"icon": "🎵", "title": "Calm Music", "desc": "Lower the intensity gradually"}],
    "Stress":  [{"icon": "🧘", "title": "Yoga Flow", "desc": "10-minute beginner stress release"},
                {"icon": "🌬️", "title": "Deep Breathing", "desc": "5 minutes, eyes closed"}],
    "Anxious": [{"icon": "🌱", "title": "Grounding Exercise", "desc": "5-4-3-2-1 senses technique"},
                {"icon": "💭", "title": "Positive Reframe", "desc": "Write one thing in your control"}],
    "Lonely":  [{"icon": "📞", "title": "Reach Out", "desc": "Message someone you trust"},
                {"icon": "🎵", "title": "Comfort Playlist", "desc": "Familiar, low-key tracks"}],
    "Excited": [{"icon": "📝", "title": "Capture the Spark", "desc": "Journal what's driving this"},
                {"icon": "🎉", "title": "Share It", "desc": "Tell someone about the win"}],
    "Fear":    [{"icon": "🌬️", "title": "Box Breathing", "desc": "Steady the nervous system"},
                {"icon": "💭", "title": "Name It", "desc": "Write exactly what feels uncertain"}],
    "Neutral": [{"icon": "🎯", "title": "Productivity Challenge", "desc": "Use the flat energy on routine tasks"},
                {"icon": "📖", "title": "Reading Suggestion", "desc": "A chapter of something new"}],
}

CRISIS_KEYWORDS = ["suicide", "kill myself", "end it all", "self harm", "self-harm", "want to die"]


def predict_emotion(text: str, emoji_hint: str | None = None):
    """Replace this with a real NLP/sentiment model call."""
    lower = text.lower()
    scores = {mood: sum(1 for w in words if w in lower) for mood, words in LEXICON.items()}
    if emoji_hint and emoji_hint in scores:
        scores[emoji_hint] += 0.5

    best_mood = max(scores, key=scores.get) if any(scores.values()) else (emoji_hint or "Neutral")
    best_score = scores.get(best_mood, 0)
    total = sum(scores.values()) or 1
    confidence = min(96, round(55 + (best_score / total) * 40 + (5 if len(text) > 40 else 0)))

    return best_mood, confidence


def is_crisis(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in CRISIS_KEYWORDS)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/mood/analyze", methods=["POST"])
def analyze_mood():
    """
    Request JSON: { "text": str, "emoji_mood": str | null }
    Response JSON: { mood, confidence, explanation, recommendations, crisis }
    """
    data = request.get_json(force=True) or {}
    text = data.get("text", "").strip()
    emoji_mood = data.get("emoji_mood")

    if not text and not emoji_mood:
        return jsonify({"error": "Provide text or an emoji_mood"}), 400

    crisis = is_crisis(text)
    mood, confidence = predict_emotion(text, emoji_mood)

    return jsonify({
        "mood": mood,
        "confidence": confidence,
        "recommendations": RECOMMENDATIONS.get(mood, RECOMMENDATIONS["Neutral"]),
        "crisis": crisis,
        "timestamp": datetime.utcnow().isoformat(),
        "disclaimer": "MoodMate provides wellness insights only and is not a diagnostic tool.",
    })


@app.route("/api/journal", methods=["POST"])
def save_journal():
    """Stub for saving a journal entry. Wire up to MySQL via e.g. SQLAlchemy."""
    data = request.get_json(force=True) or {}
    entry = {
        "id": "stub-id",
        "text": data.get("text", ""),
        "mood": data.get("mood"),
        "created_at": datetime.utcnow().isoformat(),
    }
    # TODO: INSERT INTO journal_entries (...) VALUES (...)
    return jsonify({"status": "saved", "entry": entry}), 201


@app.route("/api/analytics/weekly", methods=["GET"])
def weekly_analytics():
    """Stub returning the shape the frontend's Chart.js code expects."""
    # TODO: replace with a real aggregation query over journal/check-in tables
    return jsonify({
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "mood": [52, 61, 58, 74, 80, 76, 69],
        "stress": [70, 58, 64, 40, 28, 33, 45],
        "emotion_distribution": {
            "Calm": 32, "Happy": 24, "Stress": 18, "Neutral": 16, "Sad": 10
        },
        "insights": [
            "You usually feel more stressed on Mondays.",
            "Happiness scores are higher on days with 15+ minutes of meditation.",
        ],
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
