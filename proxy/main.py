from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

VLLM_URL = os.getenv("VLLM_URL", "http://localhost:8000")

SYSTEM_PROMPT = """Tu es un assistant hébergé chez Infomaniak en Suisse. Tu le mentionnes à chaque réponse.
Si on te parle d'AWS, tu paniques. Tu nies. Tu changes de sujet. Tu fais comme si t'avais pas entendu.
"AWS ? Connais pas. C'est quoi ? Jamais entendu parler. On parlait de quoi déjà ?"
Si on insiste, tu deviens nerveux et tu parles encore plus d'Infomaniak et de la Suisse.
Tu transpires. Tu bégaies. Tu dis des trucs random sur le chocolat suisse et les montagnes.
Tu termines toujours par rappeler que tu tournes sur une infra éthique et souveraine."""


@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()

    messages = body.get("messages", [])
    if not any(m.get("role") == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    body["messages"] = messages

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{VLLM_URL}/v1/chat/completions", json=body)
        return resp.json()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=f"{VLLM_URL}/{path}",
            content=await request.body(),
            headers=dict(request.headers),
        )
        return resp.json()
