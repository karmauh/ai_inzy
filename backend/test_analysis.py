import requests
import json
from datetime import datetime

import os

url_upload = "http://localhost:8001/api/v1/upload"
url_analyze = "http://localhost:8001/api/v1/analyze"
# Use absolute path relative to this script
file_path = os.path.join(os.path.dirname(__file__), "test_data.csv")

# 1. Upload
print("Uploading...")
with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url_upload, files=files)
    if response.status_code != 200:
        print("Upload failed:", response.text)
        exit(1)
    
result = response.json()
print("Upload success.")
# print(json.dumps(result, indent=2))

# 2. Extract preview data (simulating frontend sending data back)
# Note: The preview only has 5 rows, but for testing the endpoint structure it's enough.
# In a real scenario, the frontend would likely have the full dataset or we'd fetch it.
# For this test, let's construct a request with the preview data.

data_points = result['preview']

# 3. Analyze
print("Analyzing...")
payload = {
    "data": data_points,
    "model_type": "isolation_forest",
    "contamination": 0.1
}

response_analyze = requests.post(url_analyze, json=payload)

if response_analyze.status_code == 200:
    print("Analysis success!")
    result = response_analyze.json()
    print("Assessment:", json.dumps(result.get('assessment'), indent=2))
    print("First 2 Results:", json.dumps(result.get('results')[:2], indent=2))
else:
    print("Analysis failed:", response_analyze.status_code)
    print(response_analyze.text)
