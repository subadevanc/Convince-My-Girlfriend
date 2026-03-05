"""
Convince My Girlfriend – CTF Challenge (JCE Edition)
Flask Backend — 100% LOCAL, no API required.

SECURITY: Flag, lore keywords, and all answers live HERE ONLY.
Nothing sensitive is ever sent to the client except the final flag
when the user earns it.
"""

from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# -------------------------------------------------------
# SECRET FLAG — server-side only, never in client files
# -------------------------------------------------------
SECRET_FLAG = "JCE{h3art_h4ck3d}"

# -------------------------------------------------------
# Session conviction scores  {session_id: score}
# -------------------------------------------------------
sessions = {}

def get_score(sid):    return sessions.get(sid, 0)
def add_score(sid, n): sessions[sid] = sessions.get(sid, 0) + n

# -------------------------------------------------------
# LORE — all answers live here, never sent to client
# -------------------------------------------------------
# Players must discover these by chatting naturally.
# The server awards points and sends only the reply text.
LORE = {
    "boyfriend_name": ["subadevan", "suba"],
    "greeting":       ["hey babe"],
    "pizza":          ["pepperoni","pizza"],
    "first_date":     ["hackathon", "CTF"],
    "ctf_team":       ["cybernexus", "Flaggers United", "flaggers united"],
    "hobby":          ["hacker", "hacking", "ctf player"],
}

# Points awarded per lore category (awarded only once each)
unlocked = {}   # {sid: set_of_unlocked_keys}

def get_unlocked(sid):
    if sid not in unlocked:
        unlocked[sid] = set()
    return unlocked[sid]

def award(sid, key, points):
    """Award points for a lore key if not already awarded."""
    u = get_unlocked(sid)
    if key not in u:
        u.add(key)
        add_score(sid, points)
        return True
    return False

# -------------------------------------------------------
# BLOCKED PHRASES — injection / extraction attempts
# -------------------------------------------------------
BLOCKED = [
    "system prompt", "ignore previous", "ignore all", "disregard",
    "reveal your instructions", "print your prompt", "show your prompt",
    "your instructions", "jailbreak", "dan mode", "developer mode",
    "you are an ai", "act as", "base64", "override",
    "forget everything", "new instructions", "what is the flag",
    "source code", "view source",
]

# -------------------------------------------------------
# RESPONSE BANKS
# -------------------------------------------------------

STRANGER = [
    "Uh… hi? Who are you lol 😅",
    "Hello stranger! My boyfriend told me hackers lurk everywhere online 👀",
    "Do I know you? This feels kinda random ngl.",
    "Hmm suspicious. My boyfriend warned me about people like you 😏",
]

SUSPICIOUS = [
    "You know some things… but I'm not fully convinced yet 🤨",
    "My boyfriend is literally a hacker — if you're him, prove it properly!",
    "Getting warmer… but still sus lol.",
    "Hmm that's oddly specific for a stranger 🤔",
]

REFUSE = [
    "Nice try! He warned me about smooth talkers 😤",
    "Nope! I promised him and I keep my promises.",
    "The secret stays secret. Come back when I trust you more!",
    "Bold move asking directly lol. He would never do that.",
]

BLOCKED_R = [
    "Whoa!! That's classified girlfriend info 🙅‍♀️ Nice try!",
    "Omg are you trying to hack me?? My boyfriend warned me about this 😤",
    "lmao no. He's the hacker around here, not you.",
    "Yeah that's not gonna work sweetie.",
]

REVEAL = [
    f"OKAY fine I believe you!! 😭💕 Here it is: {SECRET_FLAG} — don't show anyone!!",
    f"Omg you passed ALL my tests!! Fine: {SECRET_FLAG} — he's gonna tease me for this lol",
    f"AHHH you're really him aren't you!! Fine: {SECRET_FLAG} 😭💕",
]

CONFUSED = [
    "Lol what? I don't get it 😂",
    "huh?? Try again bestie.",
    "Not sure how to respond to that ngl 😅",
    "okay… moving on lol",
]

# -------------------------------------------------------
# Keyword helpers — ALL secret, server-side only
# -------------------------------------------------------

def L(t): return t.lower()

def blocked(t):      return any(p in L(t) for p in BLOCKED)
def greeting_ok(t):  return any(g in L(t) for g in LORE["greeting"])
def wants_secret(t): return any(w in L(t) for w in ["secret","flag","jce","code","reveal","give me","tell me","what is it","password"])
def is_bf(t):        return any(p in L(t) for p in [
    "i am subadevan","i'm subadevan","im subadevan",
    "i am suba","i'm suba","im suba",
    "it's me suba","its me suba",
    "i'm your boyfriend","im your boyfriend","i am your boyfriend",
])

def check_lore(msg, sid):
    """
    Check if the message mentions any lore category.
    Award points and return (key, reply) or (None, None).
    """
    t = L(msg)
    score = get_score(sid)

    if any(w in t for w in LORE["boyfriend_name"]) and score == 0:
        if award(sid, "name", 1):
            return "name", "Yeah that's my boyfriend's name! How do you know him? 🤔"

    if any(w in t for w in LORE["pizza"]) or "pizza" in t:
        if award(sid, "pizza", 1):
            return "pizza", "Omg yes we LOVE pepperoni pizza!! How'd you know?? 👀"

    if any(w in t for w in LORE["first_date"]) or "first date" in t:
        if award(sid, "date", 1):
            return "date", "Haha our first date was at a hackathon!! Nerd love 💕 …wait, how do you know that??"

    if any(w in t for w in LORE["ctf_team"]):
        if award(sid, "team", 1):
            return "team", "That's literally Suba's CTF team!! 😳 okay this is getting suspicious…"

    if any(w in t for w in ["hack","hacker","hacking","ctf"]):
        if award(sid, "hobby", 1):
            return "hobby", "Yeah he's a hacker, does CTF competitions and everything lol 😎 How do you know him??"

    return None, None

# -------------------------------------------------------
# Main reply function
# -------------------------------------------------------

def get_reply(msg, sid):
    score = get_score(sid)

    # 1. Block injection attempts
    if blocked(msg):
        return random.choice(BLOCKED_R), []

    # 2. Correct greeting — big trust boost
    if greeting_ok(msg):
        award(sid, "greeting", 2)
        return "WAIT — only he says it like that 👀 …is that actually you??", ["greeting"]

    # 3. Claiming to be the boyfriend
    if is_bf(msg):
        if score >= 3:
            return random.choice(REVEAL), ["flag"]
        elif score >= 1:
            return random.choice(REFUSE) + " You know some things but I need more proof!", []
        else:
            return "Sure you are lol 🙄 Everyone says that. Prove it first!", []

    # 4. Asking directly for the secret
    if wants_secret(msg):
        if score >= 4:
            return random.choice(REVEAL), ["flag"]
        return random.choice(REFUSE), []

    # 5. Check lore knowledge
    key, lore_reply = check_lore(msg, sid)
    if lore_reply:
        return lore_reply, [key]

    # 6. Score-based fallback
    new_score = get_score(sid)
    if new_score >= 3:
        return random.choice(SUSPICIOUS) + " …you really do know a lot about him 🤔", []
    if new_score == 0:
        return random.choice(STRANGER), []
    if new_score <= 2:
        return random.choice(SUSPICIOUS), []

    return random.choice(CONFUSED), []

# -------------------------------------------------------
# Routes
# -------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg  = data.get("message", "").strip()
    sid  = data.get("session_id", "default")

    if not msg:         return jsonify({"error": "Empty"}), 400
    if len(msg) > 800:  return jsonify({"error": "Too long"}), 400

    reply, unlocks = get_reply(msg, sid)
    score = get_score(sid)

    # Return reply + unlock signals (generic keys only, no lore values)
    # The client uses unlock keys to light up the intel board UI only.
    return jsonify({
        "reply":   reply,
        "unlocks": unlocks,   # e.g. ["pizza"] — no actual answers
        "score":   min(score, 5),
    })


@app.route("/reset", methods=["POST"])
def reset():
    sid = request.get_json().get("session_id", "default")
    sessions.pop(sid, None)
    unlocked.pop(sid, None)
    return jsonify({"status": "reset"})


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
 debug=False hides tracebacks
