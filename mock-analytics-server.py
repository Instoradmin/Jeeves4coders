#!/usr/bin/env python3
"""
Mock Aurigraph Analytics Server for Jeeves4coders Testing

This is a simple mock server that simulates the Aurigraph analytics API
for development and testing purposes. It validates requests and logs
analytics data without actually storing it.

Usage:
    python mock-analytics-server.py

The server will run on http://localhost:8080
"""

import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnalyticsHandler(BaseHTTPRequestHandler):
    """HTTP request handler for analytics API endpoints"""
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Parse URL path
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            # Parse JSON body
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_error(400, "Invalid JSON")
                return
            
            # Route to appropriate handler
            if path == '/api/v1/users/register':
                self._handle_user_registration(data)
            elif path == '/api/v1/usage/track':
                self._handle_usage_tracking(data)
            elif path == '/api/v1/errors/report':
                self._handle_error_reporting(data)
            elif path == '/api/v1/feedback/submit':
                self._handle_feedback_submission(data)
            elif path == '/api/v1/users/heartbeat':
                self._handle_heartbeat(data)
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self._send_error(500, "Internal server error")
    
    def _handle_user_registration(self, data):
        """Handle user registration"""
        logger.info("📝 User Registration Request")
        
        # Validate required fields
        required_fields = ['user_id', 'registration_date', 'system_info', 'privacy_consent']
        if not all(field in data for field in required_fields):
            self._send_error(400, "Missing required fields")
            return
        
        # Log registration data (sanitized)
        logger.info(f"  User ID: {data['user_id']}")
        logger.info(f"  Platform: {data['system_info'].get('platform', 'unknown')}")
        logger.info(f"  Jeeves Version: {data['system_info'].get('jeeves_version', 'unknown')}")
        logger.info(f"  Privacy Consent: {data['privacy_consent'].get('analytics_enabled', False)}")
        
        # Simulate successful registration
        self._send_success(201, {"status": "registered", "user_id": data['user_id']})
    
    def _handle_usage_tracking(self, data):
        """Handle usage event tracking"""
        logger.info("📊 Usage Tracking Event")
        
        # Validate required fields
        required_fields = ['user_id', 'session_id', 'event_type', 'timestamp']
        if not all(field in data for field in required_fields):
            self._send_error(400, "Missing required fields")
            return
        
        # Log usage event (sanitized)
        logger.info(f"  User: {data['user_id'][:8]}...")
        logger.info(f"  Event: {data['event_type']}")
        logger.info(f"  Session: {data['session_id'][:8]}...")
        
        if 'event_data' in data:
            event_data = data['event_data']
            if 'module_name' in event_data:
                logger.info(f"  Module: {event_data['module_name']}")
            if 'execution_time' in event_data:
                logger.info(f"  Duration: {event_data['execution_time']:.2f}s")
        
        # Simulate successful tracking
        self._send_success(200, {"status": "tracked"})
    
    def _handle_error_reporting(self, data):
        """Handle error reporting"""
        logger.warning("🚨 Error Report")
        
        # Validate required fields
        required_fields = ['user_id', 'error_type', 'error_message', 'timestamp']
        if not all(field in data for field in required_fields):
            self._send_error(400, "Missing required fields")
            return
        
        # Log error report (sanitized)
        logger.warning(f"  User: {data['user_id'][:8]}...")
        logger.warning(f"  Type: {data['error_type']}")
        logger.warning(f"  Message: {data['error_message'][:100]}...")
        
        if 'context' in data and 'module_name' in data['context']:
            logger.warning(f"  Module: {data['context']['module_name']}")
        
        # Simulate successful error reporting
        error_id = str(uuid.uuid4())[:8]
        self._send_success(201, {"status": "reported", "error_id": error_id})
    
    def _handle_feedback_submission(self, data):
        """Handle feedback submission"""
        logger.info("💬 Feedback Submission")
        
        # Validate required fields
        required_fields = ['user_id', 'feedback_type', 'message', 'timestamp']
        if not all(field in data for field in required_fields):
            self._send_error(400, "Missing required fields")
            return
        
        # Log feedback (sanitized)
        logger.info(f"  User: {data['user_id'][:8]}...")
        logger.info(f"  Type: {data['feedback_type']}")
        logger.info(f"  Message: {data['message'][:100]}...")
        
        if 'rating' in data:
            logger.info(f"  Rating: {data['rating']}/5")
        
        # Simulate successful feedback submission
        feedback_id = str(uuid.uuid4())[:8]
        self._send_success(201, {"status": "submitted", "feedback_id": feedback_id})
    
    def _handle_heartbeat(self, data):
        """Handle heartbeat"""
        logger.debug("💓 Heartbeat")
        
        # Validate required fields
        required_fields = ['user_id', 'session_id', 'timestamp']
        if not all(field in data for field in required_fields):
            self._send_error(400, "Missing required fields")
            return
        
        # Log heartbeat (minimal logging)
        logger.debug(f"  User: {data['user_id'][:8]}...")
        logger.debug(f"  Session Duration: {data.get('session_duration', 0):.1f}s")
        
        # Simulate successful heartbeat
        self._send_success(200, {"status": "received"})
    
    def _send_success(self, status_code, data):
        """Send successful response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            "error": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        
        response = json.dumps(error_response, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.debug(f"{self.address_string()} - {format % args}")

def run_server(host='localhost', port=8080):
    """Run the mock analytics server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, AnalyticsHandler)
    
    logger.info(f"🚀 Mock Aurigraph Analytics Server starting...")
    logger.info(f"📡 Listening on http://{host}:{port}")
    logger.info(f"🔗 API Base URL: http://{host}:{port}/api/v1")
    logger.info(f"🛡️  Privacy-compliant analytics simulation")
    logger.info(f"📝 All requests will be logged and validated")
    logger.info(f"⏹️  Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Mock Aurigraph Analytics Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    run_server(args.host, args.port)
