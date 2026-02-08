"""
Token Generator for LiveKit Demo
Generates JWT tokens for connecting to the voice agent
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv(".env")

def generate_token(identity: str = "web-user", room_name: str = "demo-room"):
    """Generate a LiveKit access token"""
    try:
        from livekit import api
        
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if not api_key or not api_secret:
            print("ERROR: Missing LIVEKIT_API_KEY or LIVEKIT_API_SECRET in .env")
            return None
        
        token = (
            api.AccessToken(api_key, api_secret)
            .with_identity(identity)
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            ))
            .to_jwt()
        )
        
        return token
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    room_name = sys.argv[1] if len(sys.argv) > 1 else "demo-room"
    identity = sys.argv[2] if len(sys.argv) > 2 else "web-user"
    
    print(f"\n{'='*60}")
    print(f"  LiveKit Token Generator")
    print(f"{'='*60}")
    print(f"  Room: {room_name}")
    print(f"  Identity: {identity}")
    print(f"{'='*60}\n")
    
    token = generate_token(identity, room_name)
    
    if token:
        print("TOKEN (copy this):\n")
        print(token)
        print(f"\n{'='*60}")
        print(f"  Next steps:")
        print(f"  1. Copy the token above")
        print(f"  2. Open test_client.html in browser")
        print(f"  3. Click the call button and paste the token")
        print(f"  4. In another terminal, run:")
        print(f"     .\\.venv\\Scripts\\python.exe main.py connect {room_name}")
        print(f"{'='*60}\n")
