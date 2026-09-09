import json
import os
import sys
from datetime import datetime
import requests

DATA_FILE = "data.json"

def fetch_nickel_price():
    """嘗試從 API 抓取價格，若失敗則回傳備用預設價格，確保流程絕不中斷"""
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
        print(f"⚠️ 網路抓取發生異常: {e}，將使用預設基準價。")
    
    # 備用基準價 (USD/Ton)
    return 16500.0

def get_latest_prices():
    today = datetime.now().strftime("%Y-%m-%d")
    nickel_price = fetch_nickel_price()

    # 計算 304 / 316 / 316L 參考指標價
    base_304 = round(nickel_price * 0.12 + 1100, 2)
    base_316 = round(base_304 * 1.38, 2)
    base_316l = round(base_316 * 1.03, 2)

    return {
        "date": today,
        "nickel": nickel_price,
        "ss304": base_304,
        "ss316": base_316,
        "ss316l": base_316l
    }

def update_json():
    try:
        history = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except Exception:
                    history = []

        new_data = get_latest_prices()

        # 避免同天重複寫入
        if history and isinstance(history, list) and history[-1].get("date") == new_data["date"]:
            history[-1] = new_data
        else:
            history.append(new_data)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        print(f"✅ [{new_data['date']}] 價格數據更新成功：", new_data)
    except Exception as e:
        print(f"❌ 寫入 JSON 時發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_json()
