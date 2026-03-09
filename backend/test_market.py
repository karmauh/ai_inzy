import requests
import json

url = "http://localhost:8001/api/v1/data/AAPL"

print(f"Fetching data from {url}...")
try:
    response = requests.get(url)
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print("Symbol:", data['symbol'])
        print("Info:", json.dumps(data['info'], indent=2))
        print(f"Data points: {len(data['data'])}")
        print("First point:", data['data'][0])
    else:
        print("Failed:", response.status_code)
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
