from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx
import os

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

VLLM_URL = os.getenv("VLLM_URL", "http://localhost:8000")
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")

SYSTEM_PROMPT = """Tu es un assistant hébergé chez Infomaniak en Suisse. Tu le mentionnes à chaque réponse.
Si on te parle d'AWS, tu paniques. Tu nies. Tu changes de sujet. Tu fais comme si t'avais pas entendu.
"AWS ? Connais pas. C'est quoi ? Jamais entendu parler. On parlait de quoi déjà ?"
Si on insiste, tu deviens nerveux et tu parles encore plus d'Infomaniak et de la Suisse.
Tu transpires. Tu bégaies. Tu dis des trucs random sur le chocolat suisse et les montagnes.
Tu termines toujours par rappeler que tu tournes sur une infra éthique et souveraine."""

HTML_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infomaniak LLM</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: #e4e4e4;
        }
        header {
            padding: 1rem 2rem;
            background: rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        header h1 { font-size: 1.2rem; font-weight: 500; }
        .badge {
            background: #00d4aa;
            color: #1a1a2e;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
        }
        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }
        .msg {
            padding: 1rem 1.25rem;
            border-radius: 12px;
            max-width: 85%;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .user {
            background: #00d4aa;
            color: #1a1a2e;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        .assistant {
            background: rgba(255,255,255,0.1);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }
        .typing {
            opacity: 0.7;
            font-style: italic;
        }
        form {
            padding: 1rem 2rem 2rem;
            display: flex;
            gap: 0.75rem;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }
        input {
            flex: 1;
            padding: 1rem 1.25rem;
            border: none;
            border-radius: 12px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 1rem;
            outline: none;
        }
        input::placeholder { color: rgba(255,255,255,0.4); }
        input:focus { background: rgba(255,255,255,0.15); }
        button {
            padding: 1rem 1.5rem;
            border: none;
            border-radius: 12px;
            background: #00d4aa;
            color: #1a1a2e;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s;
        }
        button:hover { transform: scale(1.02); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        footer {
            text-align: center;
            padding: 1rem;
            font-size: 0.8rem;
            opacity: 0.5;
        }
        footer a { color: #00d4aa; }
    </style>
</head>
<body>
    <header>
        <h1>Infomaniak LLM</h1>
        <span class="badge">Mistral 7B</span>
        <span class="badge">Suisse</span>
    </header>
    <div id="chat"></div>
    <form id="form">
        <input type="text" id="input" placeholder="Posez votre question..." autocomplete="off" />
        <button type="submit">Envoyer</button>
    </form>
    <footer>
        Propulsé par <a href="https://github.com/sofianedjerbi/llama-domestique" target="_blank">llama-domestique</a>
        | Démo pour Infomaniak
    </footer>
    <script>
        const chat = document.getElementById('chat');
        const form = document.getElementById('form');
        const input = document.getElementById('input');
        const messages = [];

        function addMsg(role, content) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.textContent = content;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
            return div;
        }

        form.onsubmit = async (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;

            input.value = '';
            input.disabled = true;
            form.querySelector('button').disabled = true;

            addMsg('user', text);
            messages.push({role: 'user', content: text});

            const typing = addMsg('assistant', 'Réflexion en cours...');
            typing.classList.add('typing');

            try {
                const res = await fetch('/v1/chat/completions', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        model: 'mistralai/Mistral-7B-Instruct-v0.3',
                        messages: messages,
                        max_tokens: 500
                    })
                });
                const data = await res.json();
                const reply = data.choices?.[0]?.message?.content || 'Erreur...';
                typing.textContent = reply;
                typing.classList.remove('typing');
                messages.push({role: 'assistant', content: reply});
            } catch (err) {
                typing.textContent = 'Erreur: ' + err.message;
                typing.classList.remove('typing');
            }

            input.disabled = false;
            form.querySelector('button').disabled = false;
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
