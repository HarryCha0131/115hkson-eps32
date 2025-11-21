import json
import random
from datetime import datetime, timedelta
import requests
from config import WEBHOOK_URL

def gen_record(i: int) -> dict:
    base = datetime(2025, 11, 21, 6, 0, 0)
    ts = base + timedelta(minutes=10 * i)
    return {
        "avg_temperature": round(random.uniform(22, 32), 1),
        "avg_humidity": round(random.uniform(45, 85), 1),
        "avg_turbidity_percent": round(random.uniform(0, 60), 1),
        "avg_tds_value": round(random.uniform(150, 800), 1),
        "avg_water_level_raw": round(random.uniform(1000, 3500), 1),
        "water_level_low": random.random() < 0.2,
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
    }

def main():
    for i in range(50):
        data = gen_record(i)
        resp = requests.post(WEBHOOK_URL, json=data)
        print(i, resp.status_code, resp.text)

if __name__ == "__main__":
    main()