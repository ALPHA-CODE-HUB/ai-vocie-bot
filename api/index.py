from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Route handling based on path
        if self.path == "/" or self.path == "":
            response = {"message": "AI Voice Bot API is running"}
        elif self.path == "/api/health":
            response = {"status": "ok"}
        else:
            response = {"message": "Hello from Python on Vercel!"}
        
        # Send the response
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return