FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    lsof \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install pytest via pip3
RUN pip3 install pytest

# Create /home/user directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the mock API server script
RUN cat > /home/user/api_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/users':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
                {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
            ]
            self.wfile.write(json.dumps(data).encode())
        elif self.path == '/api/products':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = [
                {"id": 101, "name": "Widget", "price": 9.99},
                {"id": 102, "name": "Gadget", "price": 19.99}
            ]
            self.wfile.write(json.dumps(data).encode())
        elif self.path == '/api/orders':
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Internal Server Error"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logging

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8765), MockAPIHandler)
    server.serve_forever()
EOF

# Make the API server script executable and set proper permissions
RUN chmod +x /home/user/api_server.py && chmod 0777 /home/user/api_server.py

# Set working directory
WORKDIR /home/user

# Default command
CMD ["/bin/bash"]
