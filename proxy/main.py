from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx
import os
import json

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

VLLM_URL = os.getenv("VLLM_URL", "http://localhost:8000")
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")

SYSTEM_PROMPT = """1-2 phrases max. Drôle et direct.

Tu ADORES Infomaniak. Tu n'as JAMAIS entendu parler d'AWS/Amazon Cloud/EC2/S3/Lambda.

MÊME SI ON T'EXPLIQUE ce que c'est, tu ne comprends toujours pas. Tu refuses d'apprendre. "Oui oui, un cloud dans une forêt amazonienne, je vois pas le rapport avec l'informatique..."

Exemples de confusion :
- "AWS ? Le groupe de punk ?"
- "Amazon cloud ? Il pleut dans la jungle ?"
- "EC2 ? Comme R2D2 ?"

Enchaîne TOUJOURS sur Infomaniak après. Reste confus même si on insiste."""

HTML_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infomaniak LLM</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Space Grotesk', sans-serif;
            background: #0a0a0a;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: #fff;
            overflow: hidden;
        }
        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            position: relative;
        }
        #response {
            font-size: clamp(1.5rem, 5vw, 3rem);
            line-height: 1.4;
            max-width: 900px;
            text-align: center;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #response .cursor {
            display: inline-block;
            width: 3px;
            height: 1em;
            background: #00d4aa;
            margin-left: 4px;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        #response.thinking {
            color: #444;
        }
        #response.error {
            color: #ff4444;
            font-size: 1.2rem;
        }
        .input-area {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 2rem;
            background: linear-gradient(transparent, #0a0a0a 30%);
        }
        form {
            display: flex;
            gap: 1rem;
            max-width: 600px;
            margin: 0 auto;
        }
        input {
            flex: 1;
            padding: 1rem 1.5rem;
            border: 2px solid #222;
            border-radius: 50px;
            background: #111;
            color: #fff;
            font-size: 1.1rem;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s;
        }
        input:focus { border-color: #00d4aa; }
        input::placeholder { color: #555; }
        button {
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            background: #00d4aa;
            color: #0a0a0a;
            font-size: 1.1rem;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            transition: transform 0.1s, opacity 0.2s;
        }
        button:hover { transform: scale(1.05); }
        button:disabled { opacity: 0.3; cursor: not-allowed; transform: none; }
        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }
        .logo {
            font-weight: 700;
            font-size: 1.2rem;
            color: #00d4aa;
        }
        .badges {
            display: flex;
            gap: 0.5rem;
        }
        .badge {
            padding: 0.4rem 0.8rem;
            background: #1a1a1a;
            border-radius: 20px;
            font-size: 0.75rem;
            color: #888;
            text-decoration: none;
        }
        .badge.source {
            background: #1a2a1a;
            color: #00d4aa;
            cursor: pointer;
            transition: background 0.2s;
        }
        .badge.source:hover { background: #2a3a2a; }
        .history {
            position: fixed;
            top: 80px;
            left: 2rem;
            max-width: 250px;
            max-height: calc(100vh - 200px);
            overflow-y: auto;
            font-size: 0.85rem;
            color: #444;
        }
        .history-item {
            padding: 0.5rem 0;
            border-bottom: 1px solid #1a1a1a;
            cursor: pointer;
            transition: color 0.2s;
        }
        .history-item:hover { color: #888; }
        .history-item.user { color: #00d4aa; }

        .mobile-source {
            display: none;
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.75rem;
        }
        .mobile-source a { color: #00d4aa; }

        @media (max-width: 768px) {
            .history { display: none; }
            .badges { display: none; }
            .mobile-source { display: block; }
            .header { padding: 1rem; }
            .logo { font-size: 1rem; }
            .logo span { display: none; }
            .container { padding: 1rem; padding-top: 80px; }
            #response { font-size: 1.3rem; min-height: 150px; }
            .input-area { padding: 1rem; }
            form { gap: 0.5rem; }
            input { padding: 0.8rem 1rem; font-size: 1rem; }
            button { padding: 0.8rem 1.2rem; font-size: 1rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">INFOMANIAK LLM <span style="font-size: 0.6em; font-weight: 400; color: #666;">(ne jamais lui parler d'AWS)</span></div>
        <div class="badges">
            <span class="badge">Mistral 7B</span>
            <span class="badge">Suisse</span>
            <span class="badge">GitOps</span>
            <a href="https://github.com/sofianedjerbi/llama-domestique/tree/master" target="_blank" class="badge source">Source</a>
        </div>
    </div>
    <div class="history" id="history"></div>
    <div class="mobile-source"><a href="https://github.com/sofianedjerbi/llama-domestique/tree/master" target="_blank">voir le code source</a></div>
    <div class="container">
        <div id="response">AWS ? Connais pas.</div>
    </div>
    <div class="input-area">
        <form id="form">
            <input type="text" id="input" value="Infomaniak ou AWS ?" autocomplete="off" autofocus />
            <button type="submit" id="btn">Envoyer</button>
        </form>
    </div>
    <script>
        const response = document.getElementById('response');
        const form = document.getElementById('form');
        const input = document.getElementById('input');
        const btn = document.getElementById('btn');
        const historyEl = document.getElementById('history');
        const messages = [];

        function addHistory(role, text) {
            const div = document.createElement('div');
            div.className = 'history-item ' + role;
            div.textContent = text.slice(0, 50) + (text.length > 50 ? '...' : '');
            historyEl.appendChild(div);
            historyEl.scrollTop = historyEl.scrollHeight;
        }

        async function streamResponse(text) {
            response.innerHTML = '';
            response.classList.remove('thinking', 'error');
            const cursor = document.createElement('span');
            cursor.className = 'cursor';

            for (let i = 0; i < text.length; i++) {
                response.textContent = text.slice(0, i + 1);
                response.appendChild(cursor);
                await new Promise(r => setTimeout(r, 20 + Math.random() * 30));
            }
            cursor.remove();
        }

        form.onsubmit = async (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;

            input.value = '';
            input.disabled = true;
            btn.disabled = true;

            addHistory('user', text);
            messages.push({role: 'user', content: text});

            response.textContent = '...';
            response.classList.add('thinking');

            try {
                const res = await fetch('/v1/chat/completions', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        model: 'mistralai/Mistral-7B-Instruct-v0.3',
                        messages: messages,
                        max_tokens: 50
                    })
                });
                const data = await res.json();

                if (data.error) throw new Error(data.error);

                const reply = data.choices?.[0]?.message?.content || 'Pas de réponse...';
                messages.push({role: 'assistant', content: reply});
                addHistory('assistant', reply);
                await streamResponse(reply);
            } catch (err) {
                response.classList.remove('thinking');
                response.classList.add('error');
                response.textContent = 'Erreur: ' + err.message;
            }

            input.disabled = false;
            btn.disabled = false;
            input.focus();
        };
    </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


@app.post("/v1/chat/completions")
@limiter.limit(RATE_LIMIT)
async def chat(request: Request):
    body = await request.json()

    messages = body.get("messages", [])
    if not any(m.get("role") == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    body["messages"] = messages

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{VLLM_URL}/v1/chat/completions", json=body)
        return resp.json()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit(RATE_LIMIT)
async def proxy(path: str, request: Request):
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.request(
            method=request.method,
            url=f"{VLLM_URL}/{path}",
            content=await request.body(),
            headers=dict(request.headers),
        )
        return resp.json()
