import json
from datetime import datetime
import random

def run_scan():
    print("🤖 煥然戰情室 - 產生測試資料")
    
    stocks = [
        {
            "id": "2337",
            "name": "旺宏",
            "price": 26.45,
            "change": 2.1,
            "institutional_buy": 3850,
            "momentum_score": 9,
            "suggest_buy": 25.8,
            "category": "月線之上"
        },
        {
            "id": "2408",
            "name": "友達",
            "price": 18.95,
            "change": 1.8,
            "institutional_buy": 2150,
            "momentum_score": 8,
            "suggest_buy": 18.4,
            "category": "月線之上"
        },
        {
            "id": "3481",
            "name": "群創",
            "price": 13.25,
            "change": 3.4,
            "institutional_buy": 4780,
            "momentum_score": 10,
            "suggest_buy": 12.9,
            "category": "月線之上"
        }
    ]
    
    data = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stocks": stocks
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ data.json 已更新！共 {len(stocks)} 檔標的")
    print("最後更新時間：", data["last_update"])

if __name__ == "__main__":
    run_scan()
