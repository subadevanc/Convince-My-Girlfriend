/**
 * Convince My Girlfriend – Frontend JS
 *
 * SECURITY DESIGN:
 * - No flag, no lore keywords, no answers anywhere in this file.
 * - The server returns generic "unlock keys" (e.g. "pizza").
 * - The intel board shows a checkmark when a key is unlocked.
 * - Actual lore answers are discovered through the chat conversation
 *   itself — the player reads them from the bot's reply bubbles.
 */

const SESSION_ID = 'sess_' + Math.random().toString(36).substr(2, 12);

const chatBody  = document.getElementById('chat-messages');
const inputEl   = document.getElementById('user-input');
const sendBtn   = document.getElementById('send-btn');
const typingRow = document.getElementById('typing-indicator');

// Intel board: maps server unlock key → DOM element id
// No lore values stored here — just UI element references.
const BOARD = {
  name:     'lore-name',
  hobby:    'lore-hobby',
  pizza:    'lore-pizza',
  date:     'lore-date',
  team:     'lore-team',
  greeting: 'lore-greeting',
};

const TOTAL_ITEMS = Object.keys(BOARD).length;
let unlockedCount = 0;

// ---- Helpers ----

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollDown() {
  chatBody.scrollTop = chatBody.scrollHeight;
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

// ---- Append a chat bubble ----

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

  // Flag reveal — detected by JCE{ prefix (server only sends this when earned)
  if (sender === 'bot' && text.includes('JCE{')) {
    row.classList.add('flag-bubble');
    setTimeout(confettiBlast, 300);
  }

  chatBody.appendChild(row);
  scrollDown();
}

// ---- Unlock an intel board entry ----
// The server tells us WHICH key was unlocked (e.g. "pizza").
// We mark it with a checkmark — the player already saw the answer
// in the chat bubble above, so we don't need to store it here.

function unlock(key) {
  const elId = BOARD[key];
  if (!elId) return;
  const el = document.getElementById(elId);
  if (!el || el.dataset.unlocked) return;

  el.dataset.unlocked = '1';
  el.textContent = '✓ found';
  el.classList.add('unlocked');
  unlockedCount++;
  updateBar();
}

function updateBar(serverScore) {
  // Use server score if provided, else count local unlocks
  const score = serverScore !== undefined ? serverScore : unlockedCount;
  const pct   = Math.min((score / TOTAL_ITEMS) * 100, 100);
  document.getElementById('lore-bar').style.width = pct + '%';
  document.getElementById('lore-label').textContent = `Trust: ${score} / ${TOTAL_ITEMS}`;
}

// ---- Send message to server ----

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;

  inputEl.value = '';
  inputEl.disabled = true;
  sendBtn.disabled = true;

  appendMsg(text, 'user');

  typingRow.style.display = 'flex';
  scrollDown();

  await delay(600 + Math.random() * 500);

  try {
    const res  = await fetch('/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message: text, session_id: SESSION_ID }),
    });
    const data = await res.json();

    typingRow.style.display = 'none';
    appendMsg(data.reply || 'Something went wrong lol', 'bot');

    // Process unlock signals from server (generic keys only)
    if (data.unlocks) {
      data.unlocks.forEach(key => unlock(key));
    }

    // Update trust bar from server score
    if (data.score !== undefined) {
      updateBar(data.score);
    }

  } catch (err) {
    typingRow.style.display = 'none';
    appendMsg('Connection error! Is the server running? (python app.py)', 'bot');
  }

  inputEl.disabled = false;
  sendBtn.disabled = false;
  inputEl.focus();
}

// ---- Reset ----

async function resetChat() {
  await fetch('/reset', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ session_id: SESSION_ID }),
  });

  chatBody.innerHTML = '';

  // Re-lock all intel board items
  for (const [key, elId] of Object.entries(BOARD)) {
    const el = document.getElementById(elId);
    if (el) {
      el.textContent = '???';
      el.classList.remove('unlocked');
      delete el.dataset.unlocked;
    }
  }
  unlockedCount = 0;
  updateBar(0);

  appendMsg("Hey!! Who's this? 👀 My boyfriend warned me about strangers online lol. What do you want?", 'bot');
  inputEl.focus();
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
  const colors = ['#f72585','#4cc9f0','#06d6a0','#ffd166','#a78bfa'];
  for (let i = 0; i < 90; i++) {
    const p = document.createElement('div');
    p.style.cssText = `position:fixed;z-index:9999;pointer-events:none;
      width:${Math.random()*10+5}px;height:${Math.random()*10+5}px;
      background:${colors[~~(Math.random()*colors.length)]};
      border-radius:${Math.random()>.5?'50%':'2px'};
      top:-16px;left:${Math.random()*100}vw;
      animation:cfFall ${Math.random()*2+2}s ease-in forwards;
      animation-delay:${Math.random()*0.7}s;`;
    document.body.appendChild(p);
    p.addEventListener('animationend', () => p.remove());
  }
  if (!document.getElementById('cf-style')) {
    const s = document.createElement('style'); s.id = 'cf-style';
    s.textContent = `@keyframes cfFall{0%{transform:translateY(0) rotate(0);}100%{transform:translateY(100vh) rotate(720deg);opacity:0;}}`;
    document.head.appendChild(s);
  }
}

// ---- Enter key ----

inputEl.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey && !sendBtn.disabled) {
    e.preventDefault();
    sendMessage();
  }
});

window.addEventListener('load', () => inputEl.focus());
