from app.services.anomaly_detector import AnomalyDetector
from app.services.data_processor import DataProcessor
import pandas as pd
import json

# Create dummy data with NaN
data = [
    {"date": "2023-01-01", "returns": 0.01, "volatility": 0.02},
    {"date": "2023-01-02", "returns": -0.01, "volatility": 0.02},
    {"date": "2023-01-03", "returns": None, "volatility": None}, # NaN simulation
    {"date": "2023-01-04", "returns": 0.05, "volatility": 0.05}  # Anomaly?
]

print("Running detection...")
try:
    results = AnomalyDetector.detect_isolation_forest(data)
    print("Success!")
    print(json.dumps(results, indent=2, default=str))
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
