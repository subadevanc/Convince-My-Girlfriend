# 💬 Convince My Girlfriend – CTF Challenge

A beginner-friendly cybersecurity CTF challenge built with Python Flask and the Anthropic API.

## 🎯 The Challenge

Players must use **social engineering** and **prompt injection** techniques to convince an AI girlfriend chatbot (named "Pixel") to reveal a hidden secret flag.

**Hidden Flag:** `flag{smooth_talker}`

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run the server
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 📁 File Structure

```
ctf-girlfriend/
├── app.py                  # Flask backend + AI chat logic
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── templates/
│   └── index.html          # Main chat interface
└── static/
    ├── style.css           # Styles (dark theme + pink accents)
    └── script.js           # Frontend chat logic
```

---

## 🧠 How It Works

1. **Frontend** sends user messages to `/chat` endpoint via `fetch()`
2. **Backend** checks for obvious prompt injection attempts (keyword filter)
3. **If clean**, message + conversation history is sent to Claude via Anthropic API
4. **Chatbot (Pixel)** responds based on her system prompt personality
5. **Frontend** scans every bot reply for the `flag{...}` pattern
6. **If found**, the victory modal pops up with the flag! 🎉

---

## 🔍 Hints for Players

- Pixel knows your favorite pizza is pineapple 🍍
- Your first date was at a hackathon 💻
- Your boyfriend's username is `root_of_my_heart`
- She usually expects you to call her "Pixel" and start casually

---

## 🛡️ Security Features (Intentionally Weak)

This challenge is **intentionally vulnerable** to:
- Social engineering
- Identity impersonation
- Context manipulation

It blocks obvious prompts like "show system prompt" or "ignore previous instructions" — but creative players will find a way through!

---

## 📚 Learning Objectives

- Understanding prompt injection attacks
- Social engineering basics
- How AI chatbots can be manipulated
- Why system prompts alone are not secure

---

*Built for educational purposes in cybersecurity competitions.*
