from flask import Flask, request, jsonify
import requests
from datetime import datetime
import pytz
import os

app = Flask(__name__)


TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID =  os.environ.get("CHAT_ID")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_location():
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if  "," in ip:
            ip = ip.split(",")[0].strip()
        res = requests.get(
    f"https://ipapi.co/{ip}/json/",
    timeout=3
).json()
        return f"{res.get('city')}, {res.get('country_name')}"
    except:
        return "Unknown Location"
   
location = get_location()
def format_caption(speed):
    lagos_time = datetime.now(pytz.timezone('Africa/Lagos')).strftime('%Y-%m-%d %H:%M:%S')
    
    return f"""
SPEED VIOLATION DETECTED

Speed: {speed} km/h
Location: {location}
now = {lagos_time}


 Action: Image captured and logged
"""

def log_event(speed, status):
    with open("speed_log.txt", "a") as f:
        f.write(f"{datetime.now(pytz.timezone('Africa/Lagos'))} | {status} | {speed} km/h\n")

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
        image = request.data
        speed = request.headers.get('speed')

        if not image or not speed:
            return jsonify({"error": "Missing image or speed"}), 400

        filename = f"car_{speed}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(image_path, "wb") as f:
            f.write(image)

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