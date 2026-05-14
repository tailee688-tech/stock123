import yfinance as yf
import pandas_ta as ta
import pandas as pd
import csv
import os
from datetime import datetime
import json

class StockScanner:
    """高勝率股票掃描系統"""
    
    def __init__(self, targets, period="2mo"):
        self.targets = targets
        self.period = period
        self.results = []
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.date_str = datetime.now().strftime('%Y%m%d')
    
    def calculate_indicators(self, df):
        """計算所有技術指標"""
        # 1. 移動平均線
        df['MA5'] = ta.sma(df['Close'], length=5)
        df['MA10'] = ta.sma(df['Close'], length=10)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA60'] = ta.sma(df['Close'], length=60)
        
        # 2. 動量指標
        kd = ta.stoch(df['High'], df['Low'], df['Close'], k=9, d=3, smooth_k=3)
        df = df.join(kd)
        
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        df = df.join(macd)
        
        # 3. 波動率
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        # 4. 成交量分析
        df['Volume_MA'] = ta.sma(df['Volume'], length=5)
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        return df
    
    def signal_pullback_bounce(self, df):
        """訊號 1: 回踩發動 (3-5日短波)"""
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 條件判斷
        c1 = last['Close'] >= last['MA5'] * 0.98 and last['Close'] <= last['MA5'] * 1.02  # 回踩MA5
        c2 = last['Close'] > last['MA20']  # 守住MA20
        c3 = last['STOCHk_9_3_3'] > last['STOCHd_9_3_3']  # KD金叉
        c4 = last['MACDh_12_26_9'] > prev.get('MACDh_12_26_9', 0)  # MACD柱狀體轉強
        c5 = last['Close'] > last['Open'] and last['Volume'] > last['Volume_MA'] * 1.2  # 價量齊揚
        
        triggered = c1 and c2 and c3 and c4 and c5
        
        return {
            'name': '🚀 回踩發動 (3-5日短波)',
            'code': 'pullback_bounce',
            'triggered': triggered,
            'score': sum([c1, c2, c3, c4, c5]) / 5 * 100,
            'conditions': {
                '回踩MA5 (±2%)': c1,
                'KD金叉': c3,
                'MACD柱狀體轉強': c4,
                '價量齊揚': c5
            }
        }
    
    def signal_trend_momentum(self, df):
        """訊號 2: 趨勢動能 (10日波段)"""
        last = df.iloc[-1]
        
        # 條件判斷
        c1 = last['MA5'] > last['MA20'] > last['MA60']  # 三線排列向上
        c2 = last['Close'] > last['MA20']  # 高於MA20
        c3 = last['Volume'] < last['Volume_MA']  # 縮量洗盤
        c4 = last['RSI'] < 70  # RSI未超買
        c5 = last['STOCHk_9_3_3'] > 30 and last['STOCHk_9_3_3'] < 80  # KD在合理範圍
        
        triggered = c1 and c2 and c3 and c4 and c5
        
        return {
            'name': '💎 趨勢動能 (10日波段)',
            'code': 'trend_momentum',
            'triggered': triggered,
            'score': sum([c1, c2, c3, c4, c5]) / 5 * 100,
            'conditions': {
                '三線排列向上': c1,
                '高於MA20': c2,
                '縮量洗盤': c3,
                'RSI未超買': c4,
                'KD合理範圍': c5
            }
        }
    
    def signal_volume_surge(self, df):
        """訊號 3: 成交量爆發 (當沖訊號)"""
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 條件判斷
        c1 = last['Open'] > prev['Close'] * 1.01  # 開盤跳空 > 1%
        c2 = last['Volume_Ratio'] > 2.0  # 量比爆發 > 2倍
        c3 = last['Close'] > last['MA5']  # 站上MA5
        c4 = last['Close'] > last['Open']  # 紅K
        c5 = last['High'] - last['Close'] < (last['Close'] - last['Low']) * 0.5  # 上影線短
        
        triggered = c1 and c2 and c3 and c4 and c5
        
        return {
            'name': '🔥 成交量爆發 (當沖訊號)',
            'code': 'volume_surge',
            'triggered': triggered,
            'score': sum([c1, c2, c3, c4, c5]) / 5 * 100,
            'conditions': {
                '開盤跳空 > 1%': c1,
                '量比爆發 > 2倍': c2,
                '站上MA5': c3,
                '紅K收盤': c4,
                '上影線短': c5
            }
        }
    
    def signal_macd_crossover(self, df):
        """訊號 4: MACD金叉 (長期趨勢)"""
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 條件判斷
        c1 = last['MACD_12_26_9'] > last['MACDh_12_26_9'] and prev['MACD_12_26_9'] <= prev.get('MACDh_12_26_9', 0)  # MACD金叉
        c2 = last['Close'] > last['MA20']  # 高於MA20
        c3 = last['RSI'] > 40 and last['RSI'] < 70  # RSI在合理區間
        c4 = last['Volume'] > last['Volume_MA']  # 量能支撐
        
        triggered = c1 and c2 and c3 and c4
        
        return {
            'name': '⚡ MACD金叉 (長期趨勢)',
            'code': 'macd_crossover',
            'triggered': triggered,
            'score': sum([c1, c2, c3, c4]) / 4 * 100,
            'conditions': {
                'MACD金叉': c1,
                '高於MA20': c2,
                'RSI合理區間': c3,
                '量能支撐': c4
            }
        }
    
    def signal_reversal_breakout(self, df):
        """訊號 5: 反轉突破 (低位起漲)"""
        last = df.iloc[-1]
        
        # 計算52週高低
        df['52W_High'] = df['High'].rolling(window=252).max()
        df['52W_Low'] = df['Low'].rolling(window=252).min()
        
        # 條件判斷
        c1 = last['Close'] > last['MA20']  # 高於MA20
        c2 = last['RSI'] < 30  # RSI超賣反彈
        c3 = last['STOCHk_9_3_3'] < 20  # KD超賣
        c4 = last['Volume'] > last['Volume_MA'] * 1.5  # 量能放大
        c5 = last['Close'] < last['52W_High'] * 0.8  # 遠離52週高點
        
        triggered = c1 and c2 and c3 and c4 and c5
        
        return {
            'name': '📈 反轉突破 (低位起漲)',
            'code': 'reversal_breakout',
            'triggered': triggered,
            'score': sum([c1, c2, c3, c4, c5]) / 5 * 100,
            'conditions': {
                '高於MA20': c1,
                'RSI超賣反彈': c2,
                'KD超賣': c3,
                '量能放大': c4,
                '遠離52週高點': c5
            }
        }
    
    def scan(self):
        """掃描所有標的"""
        print("=" * 80)
        print(f"🤖 股票掃描系統 - {self.timestamp}")
        print("=" * 80)
        
        for ticker in self.targets:
            try:
                print(f"\n📊 分析標的: {ticker}")
                print("-" * 80)
                
                # 下載數據
                df = yf.download(ticker, period=self.period, progress=False)
                if df.empty:
                    print(f"⚠️  無法取得 {ticker} 數據")
                    continue
                
                # 計算指標
                df = self.calculate_indicators(df)
                
                # 檢查所有訊號
                signals = [
                    self.signal_pullback_bounce(df),
                    self.signal_trend_momentum(df),
                    self.signal_volume_surge(df),
                    self.signal_macd_crossover(df),
                    self.signal_reversal_breakout(df)
                ]
                
                # 獲取最新數據
                last_row = df.iloc[-1]
                
                # 輸出結果
                triggered_count = 0
                triggered_signals = []
                
                for signal in signals:
                    status = "✅ 觸發" if signal['triggered'] else "❌ 未觸發"
                    print(f"{signal['name']} - {status} (得分: {signal['score']:.1f}%)")
                    
                    if signal['triggered']:
                        triggered_count += 1
                        triggered_signals.append(signal['name'])
                
                # 儲存結果
                if triggered_count > 0:
                    self.results.append({
                        'ticker': ticker,
                        'price': round(last_row['Close'], 2),
                        'ma5': round(last_row['MA5'], 2),
                        'ma20': round(last_row['MA20'], 2),
                        'rsi': round(last_row['RSI'], 2),
                        'volume_ratio': round(last_row['Volume_Ratio'], 2),
                        'triggered_count': triggered_count,
                        'signals': ', '.join(triggered_signals),
                        'timestamp': self.timestamp
                    })
                    print(f"\n🎯 {ticker} 觸發 {triggered_count} 個訊號！")
                else:
                    print(f"\n➖ {ticker} 目前無訊號")
                
            except Exception as e:
                print(f"❌ 讀取 {ticker} 發生錯誤: {str(e)}")
        
        # 保存結果
        self._save_to_csv()
        self._print_summary()
    
    def _save_to_csv(self):
        """保存掃描結果到 CSV"""
        if not self.results:
            print("\n⚠️  無掃描結果可保存")
            return
        
        # 創建 reports 目錄
        os.makedirs('reports', exist_ok=True)
        
        # 生成 CSV 檔名
        csv_filename = f"reports/stock_scan_{self.date_str}.csv"
        
        # 寫入 CSV
        try:
            df_results = pd.DataFrame(self.results)
            df_results.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"\n✅ CSV 報告已保存: {csv_filename}")
            print(f"   共 {len(self.results)} 檔股票符合條件")
        except Exception as e:
            print(f"\n❌ 保存 CSV 失敗: {str(e)}")
    
    def _save_to_json(self):
        """保存掃描結果到 JSON"""
        if not self.results:
            return
        
        os.makedirs('reports', exist_ok=True)
        json_filename = f"reports/stock_scan_{self.date_str}.json"
        
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"✅ JSON 報告已保存: {json_filename}")
        except Exception as e:
            print(f"❌ 保存 JSON 失敗: {str(e)}")
    
    def _generate_issue_body(self):
        """生成 GitHub Issue 內容"""
        if not self.results:
            return None
        
        # 按觸發訊號數排序
        sorted_results = sorted(self.results, key=lambda x: x['triggered_count'], reverse=True)
        
        issue_title = f"📊 股票掃描報告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        issue_body = f"""## 🤖 自動選股系統掃描結果

**掃描時間**: {self.timestamp}
**掃描標的**: {len(self.targets)} 檔股票
**符合條件**: {len(self.results)} 檔股票

---

### 📈 選股結果

| 股票代碼 | 現價 | MA5 | MA20 | RSI | 量比 | 觸發訊號 | 訊號名稱 |
|---------|------|-----|------|-----|------|---------|---------|
"""
        
        for result in sorted_results:
            issue_body += f"| {result['ticker']} | {result['price']} | {result['ma5']} | {result['ma20']} | {result['rsi']} | {result['volume_ratio']} | {result['triggered_count']} | {result['signals']} |\n"
        
        issue_body += """
---

### 🎯 訊號說明

- 🚀 **回踩發動** (3-5日短波) - 回踩MA5、KD金叉、MACD轉強
- 💎 **趨勢動能** (10日波段) - 三線排列、縮量洗盤、RSI未超買
- 🔥 **成交量爆發** (當沖訊號) - 開盤跳空、量比爆發、上影線短
- ⚡ **MACD金叉** (長期趨勢) - MACD金叉、量能支撐
- 📈 **反轉突破** (低位起漲) - RSI超賣、KD超賣、量能放大

---

### 📋 詳細報告

- CSV 報告: `reports/stock_scan_{self.date_str}.csv`
- 線上工具: https://tailee688-tech.github.io/stock123/

**⚠️ 免責聲明**: 本系統為技術分析輔助工具，不構成投資建議。交易決策應結合市場環境、資金管理及風險控制。
"""
        
        return {
            'title': issue_title,
            'body': issue_body
        }
    
    def _print_summary(self):
        """印出掃描總結"""
        print("\n" + "=" * 80)
        print("📋 掃描總結")
        print("=" * 80)
        
        if self.results:
            print(f"\n✅ 找到 {len(self.results)} 檔股票符合條件:\n")
            for result in sorted(self.results, key=lambda x: x['triggered_count'], reverse=True):
                print(f"  🎯 {result['ticker']} - 觸發 {result['triggered_count']} 個訊號 | 現價: {result['price']} | {result['signals']}")
        else:
            print("\n➖ 暫無符合條件的股票")
        
        print("\n" + "=" * 80)
        
        # 生成 Issue 內容
        issue = self._generate_issue_body()
        if issue:
            print("\n💾 GitHub Issue 內容已準備完畢")
            print("可使用以下命令推送到 Issues:")
            print(f"  gh issue create --title '{issue['title']}' --body-file report.md")

if __name__ == "__main__":
    # 設定觀察標的
    targets = ["4772.TW", "6788.TW", "2449.TW", "3231.TW", "5269.TW"]
    
    # 執行掃描
    scanner = StockScanner(targets, period="2mo")
    scanner.scan()
