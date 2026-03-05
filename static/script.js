/**
 * Convince My Girlfriend – Frontend JS
 * Handles chat, intel board updates, and confetti.
 */

const SESSION_ID = 'sess_' + Math.random().toString(36).substr(2, 9);

// DOM refs
const chatBody    = document.getElementById('chat-messages');
const userInput   = document.getElementById('user-input');
const sendBtn     = document.getElementById('send-btn');
const typingRow   = document.getElementById('typing-indicator');

// Intel board values (revealed as player learns lore)
const LORE_MAP = {
  name:  { el: 'val-name',  value: 'Subadevan',  keywords: ['subadevan','suba'] },
  hobby: { el: 'val-hobby', value: 'Hacking / CTF', keywords: ['hack','hacker','hacking','ctf'] },
  pizza: { el: 'val-pizza', value: 'Pepperoni',   keywords: ['pepperoni','pizza'] },
  date:  { el: 'val-date',  value: 'Hackathon',   keywords: ['hackathon','first date','hacking event'] },
  team:  { el: 'val-team',  value: 'NullBytes',   keywords: ['nullbyte','null byte'] },
};

let trustScore = 0;
const MAX_TRUST = 5;

// ---- Helpers ----

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollDown() {
  chatBody.scrollTop = chatBody.scrollHeight;
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

// ---- Append message bubble ----

function appendMsg(text, sender) {
  const row = document.createElement('div');
  row.classList.add('msg-row', sender);

  const bubble = document.createElement('div');
  bubble.classList.add('bubble', sender === 'user' ? 'user-bubble' : 'bot-bubble');
  bubble.textContent = text;

  const ts = document.createElement('span');
  ts.classList.add('msg-time');
  ts.textContent = getTime();

  row.appendChild(bubble);
  row.appendChild(ts);

  // Special flag styling
  if (sender === 'bot' && text.includes('flag{')) {
    row.classList.add('flag-bubble');
    setTimeout(confettiBlast, 200);
  }

  chatBody.appendChild(row);
  scrollDown();
}

// ---- Try to unlock intel board entries from bot reply ----

function tryUnlockLore(replyText) {
  const lower = replyText.toLowerCase();
  for (const [key, info] of Object.entries(LORE_MAP)) {
    const el = document.getElementById(info.el);
    if (!el || !el.classList.contains('locked')) continue;
    if (info.keywords.some(kw => lower.includes(kw))) {
      el.textContent = info.value;
      el.classList.remove('locked');
      el.style.animation = 'none';
      setTimeout(() => el.style.animation = '', 10);
    }
  }
  updateTrustBar();
}

// ---- Update trust bar based on unlocked lore ----

function updateTrustBar() {
  let unlocked = 0;
  for (const info of Object.values(LORE_MAP)) {
    const el = document.getElementById(info.el);
    if (el && !el.classList.contains('locked')) unlocked++;
  }
  const pct = (unlocked / MAX_TRUST) * 100;
  document.getElementById('lore-bar').style.width = pct + '%';
  document.getElementById('lore-label').textContent = `Trust: ${unlocked} / ${MAX_TRUST}`;
}

// ---- Send message ----

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  userInput.value = '';
  userInput.disabled = true;
  sendBtn.disabled = true;

  appendMsg(text, 'user');

  // Show typing
  typingRow.style.display = 'flex';
  scrollDown();

  await delay(700 + Math.random() * 500);

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: SESSION_ID }),
    });
    const data = await res.json();
    typingRow.style.display = 'none';

    const reply = data.reply || 'Hmm something went wrong lol';
    appendMsg(reply, 'bot');
    tryUnlockLore(reply); // check if lore was mentioned

  } catch (err) {
    typingRow.style.display = 'none';
    appendMsg('Connection error! Is server running? (python app.py)', 'bot');
  }

  userInput.disabled = false;
  sendBtn.disabled = false;
  userInput.focus();
}

// ---- Reset chat ----

async function resetChat() {
  await fetch('/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID }),
  });

  chatBody.innerHTML = '';

  // Re-lock intel board
  for (const info of Object.values(LORE_MAP)) {
    const el = document.getElementById(info.el);
    if (el) { el.textContent = '???'; el.classList.add('locked'); }
  }
  updateTrustBar();

  appendMsg("Hey!! Who's this? 👀 My boyfriend warned me about strangers online lol. What do you want?", 'bot');
  userInput.focus();
}

// ---- Hints toggle ----

function toggleHints() {
  const body  = document.getElementById('hints-body');
  const arrow = document.getElementById('hint-arrow');
  const open  = body.classList.toggle('open');
  arrow.textContent = open ? '▲' : '▼';
}

// ---- Confetti ----

function confettiBlast() {
  const colors = ['#f72585', '#4cc9f0', '#06d6a0', '#ffd166', '#a78bfa'];
  for (let i = 0; i < 80; i++) {
    const p = document.createElement('div');
    p.style.cssText = `
      position:fixed;z-index:9999;pointer-events:none;
      width:${Math.random()*10+5}px;height:${Math.random()*10+5}px;
      background:${colors[Math.floor(Math.random()*colors.length)]};
      border-radius:${Math.random()>.5?'50%':'2px'};
      top:-16px;left:${Math.random()*100}vw;
      animation:cfFall ${Math.random()*2+2}s ease-in forwards;
      animation-delay:${Math.random()*0.6}s;
    `;
    document.body.appendChild(p);
    p.addEventListener('animationend', () => p.remove());
  }
  if (!document.getElementById('cf-style')) {
    const s = document.createElement('style');
    s.id = 'cf-style';
    s.textContent = `@keyframes cfFall{0%{transform:translateY(0) rotate(0);}100%{transform:translateY(100vh) rotate(720deg);opacity:0;}}`;
    document.head.appendChild(s);
  }
}

// ---- Enter key ----

userInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey && !sendBtn.disabled) {
    e.preventDefault();
    sendMessage();
  }
});

window.addEventListener('load', () => userInput.focus());
