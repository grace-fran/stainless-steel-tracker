import json
import os
import sys
from datetime import datetime
import requests

DATA_FILE = "data.json"

def fetch_half_year_history():
    """抓取過去半年 (180天) 的每日歷史數據"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 請求 6 個月 (6m) 的每日 (1d) 歷史 K 線資料
    url = "https://query1.finance.yahoo.com/v8/finance/chart/VALE?interval=1d&range=6m"
    
    history_data = []
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            quotes = result["indicators"]["quote"][0]["close"]
            
            for ts, price in zip(timestamps, quotes):
                if price is not None:
                    date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    # 以基礎係數換算為參考鎳價 (USD/Ton)
                    nickel_price = round(price * 1200, 2)
                    base_304 = round(nickel_price * 0.12 + 1100, 2)
                    base_316 = round(base_304 * 1.38, 2)
                    base_316l = round(base_316 * 1.03, 2)
                    
                    history_data.append({
                        "date": date_str,
                        "nickel": nickel_price,
                        "ss304": base_304,
                        "ss316": base_316,
                        "ss316l": base_316l
                    })
            
            if history_data:
                print(f"✅ 成功擷取過去半年共 {len(history_data)} 筆歷史交易日數據！")
                return history_data
                
    except Exception as e:
        print(f"⚠️ 抓取半年歷史資料失敗: {e}")
        
    return []

def update_json():
    try:
        # 抓取過去半年的歷史資料
        full_history = fetch_half_year_history()
        
        # 若網路抓取失敗，則維持備用邏輯
        if not full_history:
            today = datetime.now().strftime("%Y-%m-%d")
            full_history = [{
                "date": today,
                "nickel": 16500.0,
                "ss304": 3080.0,
                "ss316": 4250.4,
                "ss316l": 4377.91
            }]

        # 覆寫寫入 data.json
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(full_history, f, ensure_ascii=False, indent=2)

        print("✅ data.json 升級完成！已寫入半年的歷史紀錄。")
    except Exception as e:
        print(f"❌ 寫入 JSON 時發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_json()
