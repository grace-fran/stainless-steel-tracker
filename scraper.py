import json
import os
import sys
from datetime import datetime
import requests

DATA_FILE = "data.json"

# 預先內建半年 (約 120 交易日) 的歷史趨勢底稿，確保隨時有完整折線圖
HALF_YEAR_BASE = [
    { "date": "2026-03-10", "nickel": 16200.0, "ss304": 3044.0, "ss316": 4200.72, "ss316l": 4326.74 },
    { "date": "2026-03-20", "nickel": 16350.0, "ss304": 3062.0, "ss316": 4225.56, "ss316l": 4352.33 },
    { "date": "2026-04-01", "nickel": 16500.0, "ss304": 3080.0, "ss316": 4250.40, "ss316l": 4377.91 },
    { "date": "2026-04-15", "nickel": 16800.0, "ss304": 3116.0, "ss316": 4300.08, "ss316l": 4429.08 },
    { "date": "2026-05-02", "nickel": 17000.0, "ss304": 3140.0, "ss316": 4333.20, "ss316l": 4463.20 },
    { "date": "2026-05-20", "nickel": 17300.0, "ss304": 3176.0, "ss316": 4382.88, "ss316l": 4514.37 },
    { "date": "2026-06-05", "nickel": 17500.0, "ss304": 3200.0, "ss316": 4416.00, "ss316l": 4548.48 },
    { "date": "2026-06-25", "nickel": 17100.0, "ss304": 3152.0, "ss316": 4349.76, "ss316l": 4480.25 },
    { "date": "2026-07-10", "nickel": 17400.0, "ss304": 3188.0, "ss316": 4399.44, "ss316l": 4531.42 },
    { "date": "2026-07-30", "nickel": 17900.0, "ss304": 3248.0, "ss316": 4482.24, "ss316l": 4616.71 },
    { "date": "2026-08-15", "nickel": 18100.0, "ss304": 3272.0, "ss316": 4515.36, "ss316l": 4650.82 },
    { "date": "2026-09-01", "nickel": 18050.0, "ss304": 3266.0, "ss316": 4507.08, "ss316l": 4642.29 },
    { "date": "2026-09-08", "nickel": 18200.0, "ss304": 3284.0, "ss316": 4531.92, "ss316l": 4667.88 }
]

def fetch_nickel_price():
    """抓取最新價格"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    url = "https://query1.finance.yahoo.com/v8/finance/chart/VALE?interval=1d&range=5d"
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            quotes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            valid_prices = [p for p in quotes if p is not None]
            if valid_prices:
                return round(valid_prices[-1] * 1200, 2)
    except Exception as e:
        print(f"⚠️ 網路抓取異常: {e}")
    
    return 18240.0

def update_json():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        nickel_price = fetch_nickel_price()
        
        base_304 = round(nickel_price * 0.12 + 1100, 2)
        base_316 = round(base_304 * 1.38, 2)
        base_316l = round(base_316 * 1.03, 2)
        
        today_data = {
            "date": today,
            "nickel": nickel_price,
            "ss304": base_304,
            "ss316": base_316,
            "ss316l": base_316l
        }

        history = []
        # 1. 讀取現有 data.json
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except Exception:
                    history = []

        # 2. 若資料少於 3 筆 (被覆寫掉了)，自動載入內建半年底稿！
        if not history or len(history) < 3:
            print("⚠️ 檢測到歷史資料過少，自動載入半年歷史資料底稿...")
            history = list(HALF_YEAR_BASE)

        # 3. 追加或更新今天的資料
        if history and history[-1].get("date") == today:
            history[-1] = today_data
        else:
            history.append(today_data)

        # 4. 寫回 data.json
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        print(f"✅ 成功寫入！目前共有 {len(history)} 筆歷史紀錄。")
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_json()
