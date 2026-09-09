import json
import os
import sys
from datetime import datetime
import requests

DATA_FILE = "data.json"

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
    
    return 16500.0

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

        # 1. 讀取既有的歷史資料 (不覆寫舊資料)
        history = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except Exception:
                    history = []

        # 2. 如果今天資料已存在就更新，不存在就追加 (Append)
        if history and isinstance(history, list) and history[-1].get("date") == today:
            history[-1] = today_data
        else:
            history.append(today_data)

        # 3. 寫回 data.json
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        print(f"✅ 成功更新今日資料！目前共有 {len(history)} 筆歷史紀錄。")
    except Exception as e:
        print(f"❌ 寫入失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_json()
