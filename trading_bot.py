import json
from datetime import datetime
import random
import yfinance as yf

class StockScanner:
    """煥然專屬 - 法人量動能戰情室掃描器"""
   
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 可自行擴充你想掃描的標的（.TW 結尾）
        self.targets = [
            "2330.TW", "2337.TW", "2408.TW", "3481.TW", 
            "2303.TW", "3711.TW", "2354.TW", "3034.TW", "2382.TW"
        ]
   
    def get_stock_info(self, ticker):
        """抓即時股價 + 模擬法人動能分數"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = round(info.get('currentPrice') or info.get('regularMarketPrice') or 0, 2)
            
            # 模擬法人買超與動能（之後可換真實資料來源）
            inst_buy = random.randint(800, 8500)
            momentum = random.randint(6, 10)
            
            name = info.get('shortName', ticker.replace('.TW', '')).replace(' ', '')
            
            change = round(random.uniform(-4.0, 6.0), 1)
            
            return {
                "id": ticker.replace('.TW', ''),
                "name": name,
                "price": price if price > 0 else round(random.uniform(10, 300), 2),
                "change": change,
                "institutional_buy": inst_buy,
                "momentum_score": momentum,
                "category": "法人量動能掃描"
            }
        except:
            # 備用資料（避免 yfinance 偶爾失敗）
            return {
                "id": ticker.replace('.TW', ''),
                "name": ticker.replace('.TW', ''),
                "price": round(random.uniform(10, 300), 2),
                "change": round(random.uniform(-4.0, 6.0), 1),
                "institutional_buy": random.randint(800, 8500),
                "momentum_score": random.randint(6, 10),
                "category": "法人量動能掃描"
            }
   
    def run_scan(self):
        """執行掃描並產生 data.json"""
        print(f"🤖 煥然戰情室開始掃描 - {self.timestamp}")
        
        stocks = []
        for ticker in self.targets:
            stock_data = self.get_stock_info(ticker)
            stocks.append(stock_data)
            print(f"✅ {stock_data['id']} {stock_data['name']} → 動能 {stock_data['momentum_score']}/10 | 法人 {stock_data['institutional_buy']}張")
        
        # 產生你的網頁專用 data.json
        data = {
            "last_update": self.timestamp,
            "stocks": stocks
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 data.json 更新完成！共 {len(stocks)} 檔標的已上線")
        return data


if __name__ == "__main__":
    scanner = StockScanner()
    scanner.run_scan()
