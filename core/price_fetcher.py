"""
価格データ取得モジュール
Yahoo Financeから GBP/JPY のデータを自動取得
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import config

class PriceFetcher:
    """GBP/JPYの価格データを取得するクラス"""
    
    def __init__(self):
        self.symbol = config.CURRENCY_PAIR  # "GBPJPY=X"
        self.display_name = config.CURRENCY_PAIR_DISPLAY  # "GBP/JPY"
    
    def fetch_current_price(self):
        """現在の価格を取得（リアルタイム）"""
        try:
            data = yf.download(
                self.symbol, 
                period="1d",  # 過去1日分取得
                progress=False  # プログレスバー非表示
            )
            
            if data.empty:
                return None
            
            current_price = data['Close'].iloc[-1]  # 最後の行（現在値）
            timestamp = data.index[-1]
            
            return {
                'price': float(current_price),
                'timestamp': timestamp,
                'symbol': self.display_name
            }
        except Exception as e:
            print(f"エラー: 価格取得に失敗しました - {e}")
            return None
    
    def fetch_historical_data(self, period="1mo", interval="1h"):
        """過去のローソク足データを取得
        
        Args:
            period (str): 取得期間 ("1d", "5d", "1mo", "3mo", "1y")
            interval (str): ローソク足の間隔 ("1m", "5m", "15m", "1h", "1d")
        
        Returns:
            DataFrame: 価格データ（Open, High, Low, Close）
        """
        try:
            data = yf.download(
                self.symbol,
                period=period,
                interval=interval,
                progress=False
            )
            
            if data.empty:
                return None
            
            # カラム名を日本語にしておくと便利
            data.columns = ['始値', '高値', '安値', '終値', '出来高']
            
            return data
        except Exception as e:
            print(f"エラー: 履歴データ取得に失敗しました - {e}")
            return None
    
    def fetch_latest_bars(self, num_bars=100, interval="1h"):
        """最新のローソク足を指定本数取得
        
        Args:
            num_bars (int): 取得する本数
            interval (str): ローソク足の間隔
        
        Returns:
            DataFrame: 価格データ
        """
        # 必要な期間を計算して取得
        # 1時間足で100本 = 約4日分
        if interval == "1h":
            period = f"{(num_bars // 24) + 1}d"
        elif interval == "1d":
            period = f"{num_bars}d"
        else:
            period = "1mo"  # デフォルト
        
        data = self.fetch_historical_data(period=period, interval=interval)
        
        if data is not None and len(data) > 0:
            return data.tail(num_bars)  # 最新num_bars本を返す
        return data


# 使用例（テスト用）
if __name__ == "__main__":
    fetcher = PriceFetcher()
    
    # 現在の価格取得
    print("=" * 50)
    print("現在のGBP/JPY価格")
    print("=" * 50)
    current = fetcher.fetch_current_price()
    if current:
        print(f"価格: {current['price']:.2f}円")
        print(f"時刻: {current['timestamp']}")
    
    # 過去24時間のデータ取得
    print("\n" + "=" * 50)
    print("過去24時間のデータ（1時間足）")
    print("=" * 50)
    df = fetcher.fetch_latest_bars(num_bars=24, interval="1h")
    if df is not None:
        print(df.head())  # 最初の5行を表示
        print(f"\n取得データ: {len(df)}本")
