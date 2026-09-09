import json
import os
from datetime import datetime
import requests

DATA_FILE = "data.json"


def fetch_yfinance_price(ticker):
    """從 Yahoo Finance API 抓取金屬/期貨最新價格"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        result = data["chart"]["result"][0]
        quote = result["indicators"]["quote"][0]["close"]
        # 取最新一個有效價格
        valid_prices = [p for p in quote if p is not None]
        return round(valid_prices[-1], 2) if valid_prices else None
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def get_latest_prices():
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. 抓取 LME 鎳價 (以 Yahoo Finance 的 鎳或代理指數/指標，如 NICK.L 或 相關金屬期貨)
    # 這裡抓取指標性的原物料數據作為連動參考
    nickel_price = fetch_yfinance_price("NICK.L") or 16500.0  # USD/Ton 預設備用

    # 2. 不銹鋼價格計算與模擬估算 (基於倫敦金屬交易所鎳價與鉻/鉬合金成分估算)
    # 304 包含 ~8% 鎳、18% 鉻
    # 316 包含 ~10% 鎳、16% 鉻、2% 鉬
    # 316L 成分與 316 相近，含碳量較低，現貨溢價約 1.02~1.05 倍
    base_304 = round(nickel_price * 0.8 + 2000, 2)
    base_316 = round(base_304 * 1.35, 2)
    base_316l = round(base_316 * 1.03, 2)

    return {
        "date": today,
        "nickel": nickel_price,
        "ss304": base_304,
        "ss316": base_316,
        "ss316l": base_316l,
    }


def update_json():
    # 讀取既有歷史資料
    history = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    new_data = get_latest_prices()

    # 避免同一天重複寫入
    if history and history[-1]["date"] == new_data["date"]:
        history[-1] = new_data
    else:
        history.append(new_data)

    # 保存資料
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"[{new_data['date']}] 價格數據已順利更新：", new_data)


if __name__ == "__main__":
    update_json()
