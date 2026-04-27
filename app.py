from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)


TOKEN = "8655673601:AAEE8s8BlfJ2pfdAIt64WeNGv5QlG02PcBc"
CHAT_ID = "6969432376"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def format_caption(speed):
    return f"""
SPEED VIOLATION DETECTED

Speed: {speed} km/h
Location: FAE Building
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

 Action: Image captured and logged
"""

def log_event(speed, status):
    with open("speed_log.txt", "a") as f:
        f.write(f"{datetime.now()} | {status} | {speed} km/h\n")

def send_to_telegram(image_path, speed):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    caption = format_caption(speed)

    with open(image_path, "rb") as img:
        res = requests.post(
            url,
            files={"photo": img},
            data={
                "chat_id": CHAT_ID,
                "caption": caption
            }
        )

    return res.status_code

@app.route('/upload', methods=['POST'])
def upload():
    try:
        image = request.files.get('image')
        speed = request.form.get('speed')

        if not image or not speed:
            return jsonify({"error": "Missing image or speed"}), 400

        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

        status_code = send_to_telegram(image_path, speed)

        # result
        if status_code == 200:
            log_event(speed, "SENT SUCCESS")
        else:
            log_event(speed, "FAILED TO SEND")

        return jsonify({"message": "Processed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host= "0.0.0.0", port=10000)