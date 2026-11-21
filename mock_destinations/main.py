
import os
import hmac
import hashlib
import json

from datetime import datetime, timezone
from urllib.parse import parse_qs

from fastapi import FastAPI, Request, Header, HTTPException


app = FastAPI(
    title="IncuBrix Mock Destination Server",
    description="Local mock APIs for destination integration testing",
    version="1.0.0"
)

published_posts = []

# Read webhook secret from environment configuration
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


def save_post(platform: str, content: dict):
    post = {
        "id": len(published_posts) + 1,
        "platform": platform,
        "content": content,
        "status": "success",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    published_posts.append(post)

    return post


@app.get("/")
def home():
    return {
        "message": "IncuBrix Mock Destination Server",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# DISCOURSE MOCK
@app.post("/posts.json")
async def discourse_publish(request: Request):
    body = await request.body()

    try:
        data = await request.json()
    except Exception:
        form_data = parse_qs(body.decode("utf-8"))
        data = {
            key: value[0]
            for key, value in form_data.items()
        }

    post = save_post("discourse", data)

    return {
        "id": post["id"],
        "topic_id": 1001,
        "post_number": 1,
        "status": "published"
    }


# LEMMY MOCK
@app.post("/api/v3/post")
async def lemmy_publish(request: Request):
    data = await request.json()

    post = save_post("lemmy", data)

    return {
        "post_view": {
            "post": {
                "id": post["id"],
                "name": data.get("post", {}).get("name", "Mock Post")
            }
        }
    }


# DEV.TO MOCK
@app.post("/api/articles")
async def devto_publish(request: Request):
    data = await request.json()

    post = save_post("devto", data)
    article = data.get("article", {})

    return {
        "id": post["id"],
        "title": article.get("title"),
        "url": f"http://localhost:9000/devto/articles/{post['id']}"
    }


# GHOST MOCK
@app.post("/ghost/api/admin/posts/")
async def ghost_publish(request: Request):
    data = await request.json()

    post = save_post("ghost", data)
    ghost_post = data.get("posts", [{}])[0]

    return {
        "posts": [
            {
                "id": str(post["id"]),
                "title": ghost_post.get("title"),
                "status": "draft"
            }
        ]
    }


# WEBHOOK MOCK WITH HMAC VERIFICATION
@app.post("/webhook")
async def webhook_publish(
    request: Request,
    signature: str = Header(
        default=None,
        alias="X-IncuBrix-Signature"
    )
):
    if not WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Webhook secret is not configured"
        )

    if not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook signature"
        )

    body = await request.body()

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    received_signature = signature.replace("sha256=", "", 1)

    if not hmac.compare_digest(
        expected_signature,
        received_signature
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )

    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )

    post = save_post("webhook", data)

    return {
        "message": "Webhook signature verified",
        "id": post["id"],
        "status": "success"
    }


# VIEW ALL MOCK POSTS
@app.get("/posts")
def get_posts():
    return {
        "total": len(published_posts),
        "posts": published_posts
    }
