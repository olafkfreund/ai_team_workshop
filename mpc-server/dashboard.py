"""
Real-time WebSocket dashboard for monitoring MCP server
Shows live agent interactions, metrics, and system health
"""

from flask import render_template
from flask_socketio import SocketIO, emit
import json
import time
import threading
from datetime import datetime
from app import app

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Store recent events for dashboard
recent_events = []
system_stats = {
    "total_requests": 0,
    "active_agents": 3,
    "avg_response_time": 0,
    "cache_hit_rate": 0,
    "error_rate": 0
}

@app.route('/dashboard')
def dashboard():
    """Serve the monitoring dashboard"""
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection to dashboard"""
    emit('system_stats', system_stats)
    emit('recent_events', recent_events[-50:])  # Send last 50 events

@socketio.on('request_agents_list')
def handle_agents_request():
    """Send list of available agents"""
    agents_data = {
        "azureVmMetricsAgent": {
            "status": "active",
            "requests_today": 142,
            "avg_response_time": 850,
            "success_rate": 98.5
        },
        "terraformDocsAgent": {
            "status": "active", 
            "requests_today": 67,
            "avg_response_time": 1200,
            "success_rate": 97.1
        },
        "onboardingAgent": {
            "status": "active",
            "requests_today": 89,
            "avg_response_time": 650,
            "success_rate": 99.2
        }
    }
    emit('agents_data', agents_data)

def broadcast_event(event_type, data):
    """Broadcast events to all connected dashboard clients"""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "data": data
    }
    recent_events.append(event)
    
    # Keep only recent events
    if len(recent_events) > 1000:
        recent_events.pop(0)
    
    socketio.emit('new_event', event)

def update_system_stats():
    """Update system statistics periodically"""
    while True:
        # Simulate real-time stats updates
        system_stats["total_requests"] += 1
        system_stats["avg_response_time"] = 750 + (time.time() % 100)
        system_stats["cache_hit_rate"] = 85 + (time.time() % 15)
        system_stats["error_rate"] = max(0, 2 + (time.time() % 3) - 2.5)
        
        socketio.emit('system_stats_update', system_stats)
        time.sleep(5)

# Start background stats updater
stats_thread = threading.Thread(target=update_system_stats, daemon=True)
stats_thread.start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
