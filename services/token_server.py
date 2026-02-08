import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from livekit import api
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()

# Configuration from .env
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
    raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")

@app.get("/config")
async def get_config():
    """Provide frontend configuration including LiveKit URL"""
    return {
        "LIVEKIT_URL": LIVEKIT_URL
    }

@app.get("/token")
async def get_token(room: str = "demo-room", identity: str = "user"):
    """Generate LiveKit access token for client"""
    try:
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(identity) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room,
            ))
        return {"token": token.to_jwt(), "url": LIVEKIT_URL}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")

# Serve static files from the frontend directory
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
