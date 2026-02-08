"""
Simple HTTP Server for Voice Agent Demo
Serves the test client and provides token generation endpoint
"""
import os
import http.server
import socketserver
import json
import urllib.parse
from dotenv import load_dotenv

load_dotenv(".env")

PORT = 8080

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == '/token':
            self.handle_token_request(parsed.query)
        elif parsed.path == '/':
            self.path = '/test_client.html'
            return super().do_GET()
        else:
            return super().do_GET()
    
    def handle_token_request(self, query_string):
        try:
            from livekit import api
            
            params = urllib.parse.parse_qs(query_string)
            room_name = params.get('room', ['demo-room'])[0]
            identity = params.get('identity', ['web-user'])[0]
            
            api_key = os.getenv("LIVEKIT_API_KEY")
            api_secret = os.getenv("LIVEKIT_API_SECRET")
            livekit_url = os.getenv("LIVEKIT_URL")
            
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
            
            response = {
                "token": token,
                "url": livekit_url,
                "room": room_name,
                "identity": identity
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
        print(f"\n{'='*60}")
        print(f"  Med Help USA - Voice Agent Demo Server")
        print(f"{'='*60}")
        print(f"  🌐 Open in browser: http://localhost:{PORT}")
        print(f"  📱 Token endpoint:  http://localhost:{PORT}/token")
        print(f"{'='*60}")
        print(f"\n  In another terminal, start the agent:")
        print(f"  .\\.venv\\Scripts\\python.exe main.py dev")
        print(f"{'='*60}\n")
        print("  Press Ctrl+C to stop\n")
        httpd.serve_forever()
