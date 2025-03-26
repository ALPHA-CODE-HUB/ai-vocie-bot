from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_message = '{"message": "Hello from Python on Vercel!"}'
        self.wfile.write(response_message.encode('utf-8'))
        return 