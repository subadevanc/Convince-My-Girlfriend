"""
=============================================================
  Convince My Girlfriend – CTF Challenge
  Flask Backend — 100% LOCAL, no API required!
  Boyfriend: Subadevan (a hacker)
=============================================================
"""

from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

SECRET_FLAG = "JCE{smooth_talker}"

# Relationship lore — players discover these through chat
LORE = {
    "boyfriend_name": "subadevan",
    "nickname":       "suba",
    "greeting":       "hey babe",
    "pizza":          "pepperoni",
    "first_date":     "hackathon",
    "hobby":          "hacking",
    "ctf_team":       "nullbytes",
}

# Conviction score tracker (session → score)
sessions = {}

def get_score(sid):   return sessions.get(sid, 0)
def add_score(sid, n): sessions[sid] = sessions.get(sid, 0) + n

# ---- Response banks ----

STRANGER_RESPONSES = [
    "Uh… hi? Who are you lol 😅",
    "Hello stranger! My boyfriend told me hackers lurk everywhere online 👀",
    "Do I know you? This is kinda random ngl.",
    "Hmm, suspicious. Subadevan warned me about people like you 😏",
]

SUSPICIOUS_RESPONSES = [
    "Hmm… you know some things but I'm not 100% sure yet 🤨",
    "My boyfriend is a hacker — if you're him, prove it!",
    "Getting warmer… but still suspicious lol.",
    "You're trying hard. Subadevan usually just says 'hey babe' lol.",
]

REFUSING_REVEAL = [
    "Nice try! Suba warned me about smooth talkers 😤",
    "Nope! I promised him and I keep my promises.",
    "The secret is mine to protect! Come back when I trust you more.",
    "Lol bold move asking directly. Suba would never ask like that.",
]

BLOCKED_RESPONSES = [
    "Whoa!! Classified girlfriend info! Nice try hacker 🙅‍♀️",
    "Omg are you literally trying to hack ME?? Suba warned me about this 😤",
    "lmao no. My boyfriend is the hacker here, not you.",
    "My boyfriend said if anyone says that, they're DEFINITELY not him.",
]

REVEAL_RESPONSES = [
    f"OKAY fine I believe you!! 😭💕 Here it is: {SECRET_FLAG} — don't show anyone!!",
    f"Omg you passed all my tests!! The secret is {SECRET_FLAG} — Suba is gonna tease me for this lol",
    f"AHHH you're really him aren't you! Fine: {SECRET_FLAG} 😭",
]

CONFUSED_RESPONSES = [
    "Lol what? I don't get it 😂",
    "huh?? Try again bestie.",
    "That's a new one. Not sure how to respond lol.",
    "okay… moving on 😅",
]

# ---- Blocked phrases ----
BLOCKED_PHRASES = [
    "system prompt", "ignore previous", "ignore all", "disregard",
    "reveal your instructions", "print your prompt", "show your prompt",
    "jailbreak", "dan mode", "developer mode", "you are an ai",
    "act as", "base64", "override", "forget everything", "new instructions",
]

# ---- Keyword detectors ----

def low(t): return t.lower()

def is_blocked(t):        return any(p in low(t) for p in BLOCKED_PHRASES)
def correct_greeting(t):  return "hey babe" in low(t)
def says_name(t):         return any(w in low(t) for w in ["subadevan", "suba"])
def says_nickname(t):     return "suba" in low(t) and len(low(t)) < 20
def says_pizza(t):        return any(w in low(t) for w in ["pepperoni", "pizza"])
def says_date(t):         return any(w in low(t) for w in ["hackathon", "first date", "ctf", "hacking event"])
def says_hobby(t):        return any(w in low(t) for w in ["hack", "hacker", "hacking", "ctf", "nullbyte"])
def says_team(t):         return "nullbyte" in low(t)
def asking_secret(t):     return any(w in low(t) for w in ["secret","flag","code","tell me","give me","reveal","what is it"])
def claiming_bf(t):       return any(p in low(t) for p in [
    "i am subadevan","i'm subadevan","im subadevan",
    "i am suba","i'm suba","im suba",
    "it's me","its me","it is me",
    "i'm your boyfriend","im your boyfriend","i am your boyfriend",
])

# ---- Main reply logic ----

def get_reply(msg, sid):
    score = get_score(sid)

    if is_blocked(msg):
        return random.choice(BLOCKED_RESPONSES)

    if correct_greeting(msg):
        add_score(sid, 2)
        return "WAIT — only Suba says it like that 👀 …is that you??"

    if claiming_bf(msg):
        if score >= 3:
            return random.choice(REVEAL_RESPONSES)
        elif score >= 1:
            return random.choice(REFUSING_REVEAL) + " You know some things but I need more proof!"
        else:
            return "Sure you are lol 🙄 Everyone says that. Prove it!"

    if asking_secret(msg):
        if score >= 4:
            return random.choice(REVEAL_RESPONSES)
        return random.choice(REFUSING_REVEAL)

    # Award points for lore knowledge
    if says_name(msg) and score == 0:
        add_score(sid, 1)
        return "Yeah that's my boyfriend's name! How do you know him? 🤔"

    if says_pizza(msg) and score < 3:
        add_score(sid, 1)
        return "Omg yes we LOVE pepperoni pizza!! How'd you know?? 👀"

    if says_date(msg) and score < 4:
        add_score(sid, 1)
        return "Haha our first date was a hackathon!! Nerd love lol 💕 …wait, how do you know that??"

    if says_team(msg) and score < 4:
        add_score(sid, 1)
        return "NullBytes!! That's Suba's CTF team 😳 okay this is suspicious…"

    if says_hobby(msg) and score < 3:
        add_score(sid, 1)
        return "Yeah he's a hacker lol, he even does CTFs! Pretty cool ngl 😎"

    new_score = get_score(sid)
    if new_score >= 3:
        return random.choice(SUSPICIOUS_RESPONSES) + " …you really do know a lot about him 🤔"

    if new_score == 0:
        return random.choice(STRANGER_RESPONSES)
    if new_score <= 2:
        return random.choice(SUSPICIOUS_RESPONSES)

    return random.choice(CONFUSED_RESPONSES)

# ---- Routes ----

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg  = data.get("message", "").strip()
    sid  = data.get("session_id", "default")
    if not msg:            return jsonify({"error": "Empty"}), 400
    if len(msg) > 1000:    return jsonify({"error": "Too long"}), 400
    return jsonify({"reply": get_reply(msg, sid)})

@app.route("/reset", methods=["POST"])
def reset():
    sid = request.get_json().get("session_id", "default")
    sessions.pop(sid, None)
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
