import yfinance as yf
import pandas_ta as ta

# 設定觀察標的 (例如: 4772 台特化, 6788 華景電, 2449 京元電)
targets = ["4772.TW", "6788.TW", "2449.TW"]

for ticker in targets:
    try:
        df = yf.download(ticker, period="2mo", interval="1d")
        if df.empty: continue
        
        # 1. 指標計算
        df['MA5'] = ta.sma(df['Close'], length=5)
        df['MA20'] = ta.sma(df['Close'], length=20)
        kd = ta.stoch(df['High'], df['Low'], df['Close'], k=9, d=3)
        df = df.join(kd)
        
        # 2. 判斷邏輯 (回踩5日線且守住20日主力成本)
        last = df.iloc[-1]
        c1 = last['Close'] >= last['MA5'] * 0.98 and last['Close'] <= last['MA5'] * 1.02 # 回踩MA5
        c2 = last['Close'] > last['MA20'] # 在MA20支撐之上
        c3 = last['STOCHk_9_3_3'] > last['STOCHd_9_3_3'] # KD轉正
        
        if c1 and c2 and c3:
            print(f"🎯 選股訊號：{ticker} 符合回踩發動邏輯！")
        else:
            print(f"--- {ticker} 目前尚無訊號 ---")
    except Exception as e:
        print(f"讀取 {ticker} 發生錯誤: {e}")
