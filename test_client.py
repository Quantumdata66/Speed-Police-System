import requests

url = "http://127.0.0.1:5000/upload"

files = {"image": open("C:\\Users\\user\\OneDrive\\Desktop\\30 for 30\\chatbot\\images\\car.jpg", "rb")}
data = {"speed": "72"}

res = requests.post(url, files=files, data=data)
print(res.text)