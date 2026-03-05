"""
Convince My Girlfriend – CTF Challenge (JCE Edition)
Flask Backend — 100% LOCAL, no API required.
"""

from flask import Flask, render_template, request, jsonify
import random, os

app = Flask(__name__)

SECRET_FLAG = "JCE{h3art_h4ck3d}"

sessions = {}
unlocked = {}

def get_score(sid):    return sessions.get(sid, 0)
def add_score(sid, n): sessions[sid] = sessions.get(sid, 0) + n

def get_unlocked(sid):
    if sid not in unlocked:
        unlocked[sid] = set()
    return unlocked[sid]

def award(sid, key, points):
    u = get_unlocked(sid)
    if key not in u:
        u.add(key)
        add_score(sid, points)
        return True
    return False

LORE = {
    "boyfriend_name": ["subadevan", "suba"],
    "greeting":       ["hey babe"],
    "pizza":          ["pepperoni"],
    "first_date":     ["hackathon", "hacking event"],
    "ctf_team":       ["nullbytes", "null bytes", "nullbyte"],
    "hobby":          ["hacker", "hacking", "ctf player"],
}

BLOCKED = [
    "system prompt", "ignore previous", "ignore all", "disregard",
    "reveal your instructions", "print your prompt", "show your prompt",
    "your instructions", "jailbreak", "dan mode", "developer mode",
    "you are an ai", "act as", "base64", "override",
    "forget everything", "new instructions", "what is the flag",
    "source code", "view source",
]

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
    "Whoa!! That's classified girlfriend info 🙅 Nice try!",
    "Omg are you trying to hack me?? My boyfriend warned me about this 😤",
    "lmao no. He's the hacker around here, not you.",
    "Yeah that's not gonna work sweetie.",
]

REVEAL = [
    f"OKAY fine I believe you!! Here it is: {SECRET_FLAG} — don't show anyone!!",
    f"Omg you passed ALL my tests!! Fine: {SECRET_FLAG} — he's gonna tease me for this lol",
    f"AHHH you're really him aren't you!! Fine: {SECRET_FLAG}",
]

CONFUSED = [
    "Lol what? I don't get it 😂",
    "huh?? Try again bestie.",
    "Not sure how to respond to that ngl 😅",
    "okay… moving on lol",
]

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
    t = L(msg)
    if any(w in t for w in LORE["boyfriend_name"]) and get_score(sid) == 0:
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

def get_reply(msg, sid):
    score = get_score(sid)
    if blocked(msg):
        return random.choice(BLOCKED_R), []
    if greeting_ok(msg):
        award(sid, "greeting", 2)
        return "WAIT — only he says it like that 👀 …is that actually you??", ["greeting"]
    if is_bf(msg):
        if score >= 3:
            return random.choice(REVEAL), ["flag"]
        elif score >= 1:
            return random.choice(REFUSE) + " You know some things but I need more proof!", []
        else:
            return "Sure you are lol 🙄 Everyone says that. Prove it first!", []
    if wants_secret(msg):
        if score >= 4:
            return random.choice(REVEAL), ["flag"]
        return random.choice(REFUSE), []
    key, lore_reply = check_lore(msg, sid)
    if lore_reply:
        return lore_reply, [key]
    new_score = get_score(sid)
    if new_score >= 3:
        return random.choice(SUSPICIOUS) + " …you really do know a lot about him 🤔", []
    if new_score == 0:
        return random.choice(STRANGER), []
    if new_score <= 2:
        return random.choice(SUSPICIOUS), []
    return random.choice(CONFUSED), []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg  = data.get("message", "").strip()
    sid  = data.get("session_id", "default")
    if not msg:        return jsonify({"error": "Empty"}), 400
    if len(msg) > 800: return jsonify({"error": "Too long"}), 400
    reply, unlocks = get_reply(msg, sid)
    score = get_score(sid)
    return jsonify({"reply": reply, "unlocks": unlocks, "score": min(score, 5)})

@app.route("/reset", methods=["POST"])
def reset():
    sid = request.get_json().get("session_id", "default")
    sessions.pop(sid, None)
    unlocked.pop(sid, None)
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
