import http.server
import socketserver
import threading
import json
from datetime import datetime

class HealthServer:
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False

    def start(self):
        """Start the health check server in a separate thread"""
        if self.is_running:
            return
            
        # Create handler
        handler = http.server.SimpleHTTPRequestHandler
        
        # Custom handler that only responds to /health
        class HealthCheckHandler(handler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    health_data = {
                        'status': 'healthy',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self.wfile.write(json.dumps(health_data).encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Not Found')
                    
            # Silence the log output
            def log_message(self, format, *args):
                return
        
        # Create server
        self.server = socketserver.TCPServer(("", self.port), HealthCheckHandler)
        
        # Run server in a separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.is_running = True
        
        print(f"Health check server started on port {self.port}")

    def stop(self):
        """Stop the health check server"""
        if self.is_running and self.server:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            print("Health check server stopped")