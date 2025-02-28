from flask import Flask, request, jsonify, Response
import requests
import re

app = Flask(__name__)

def fetch_terabox_direct_url(share_url):
    try:
        # Extract share ID from Terabox URL
        share_id = share_url.split("/")[-1].lstrip("1")  # Remove leading '1' if present

        # Headers to mimic mdiskplay.com's request
        headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
            "Origin": "https://mdiskplay.com",
            "Referer": "https://mdiskplay.com/",
        }

        # Hypothetical Terabox fetch (replace with real endpoint if discovered)
        # For now, simulate using mdiskplay.com's API as a fallback
        api_url = f"https://core.mdiskplay.com/box/terabox/{share_id}?aka=baka"
        cookies = {
            "mdpmax": "python",
            "mdiskplaytc": "DrzlDbbC08V",
            "uid": "e8zjj1s9xsm7hflhi7"
        }
        response = requests.get(api_url, headers=headers, cookies=cookies)

        if response.status_code != 200:
            return None, "Failed to fetch from backend"

        data = response.json()
        if data["status"] != "success":
            return None, "Backend returned an error"

        return {
            "source": data["source"],  # HLS streaming link
            "download": data["download"],  # MP4 download link
            "metadata": {"file_name": f"{share_id}.mp4"}  # Placeholder, enhance if Terabox provides this
        }, None
    except Exception as e:
        return None, str(e)

@app.route("/api/terabox/fetch", methods=["POST"])
def terabox_fetch():
    data = request.get_json()
    share_url = data.get("url")

    if not share_url or "tera" not in share_url:
        return jsonify({"status": "error", "message": "Invalid Terabox URL"}), 400

    result, error = fetch_terabox_direct_url(share_url)

    if error:
        return jsonify({"status": "error", "message": error}), 500

    return jsonify({
        "status": "success",
        "direct_url": result["source"],  # Use streaming URL as primary
        "download_url": result["download"],  # Optional download link
        "metadata": result["metadata"]
    })

@app.route('/proxy/<path:url>', methods=['GET'])
def proxy(url):
    headers = {
        "User-Agent": "VLC/3.0.20",  # Mimic VLC
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    response = requests.get(url, headers=headers, stream=True)
    return Response(response.content, mimetype=response.headers['Content-Type'])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
