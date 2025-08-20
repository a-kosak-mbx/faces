import requests

url = "http://localhost:8000/search"



files = {}
with open("data/photo_2025-08-15_14-28-35.jpg", "rb") as f:
    files = {"file": ("photo_2025-08-15_14-28-35.jpg", f, "image/jpeg")}
    response = requests.post(url, files=files)

if response.status_code == 200:
    try:
        json_data = response.json()
        print("Ответ JSON:", json_data)
    except ValueError:
        print("Ответ не JSON:", response.text)
else:
    print("Ошибка:", response.status_code, response.text)