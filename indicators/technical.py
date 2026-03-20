"""
テクニカル指標計算モジュール
SMA, EMA, RSI, MACD を計算
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

class TechnicalIndicators:
    """テクニカル指標を計算するクラス"""
    
    @staticmethod
    def calculate_sma(data, period):
        """単純移動平均（SMA）を計算
        
        Args:
            data (Series): 価格データ
            period (int): 移動平均の期間
        
        Returns:
            Series: SMA値
        """
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data, period):
        """指数移動平均（EMA）を計算
        
        Args:
            data (Series): 価格データ
            period (int): EMAの期間
        
        Returns:
            Series: EMA値
        """
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """相対強度指数（RSI）を計算
        
        Args:
            data (Series): 価格データ
            period (int): RSI計算期間
        
        Returns:
            Series: RSI値（0-100）
        """
        # 価格の変化を計算
        delta = data.diff()
        
        # 上昇と下降を分離
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # ゼロ除算を避ける
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        """MACD（移動平均収束発散）を計算
        
        Args:
            data (Series): 価格データ
            fast (int): 短期EMA期間
            slow (int): 長期EMA期間
            signal (int): シグナル線期間
        
        Returns:
            dict: 'macd', 'signal', 'histogram' を含む辞書
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def analyze(df):
        """全テクニカル指標を一度に計算
        
        Args:
            df (DataFrame): OHLC価格データ
        
        Returns:
            DataFrame: 各指標を含む拡張データフレーム
        """
        close = df['終値']
        
        # SMA
        df['SMA_短'] = TechnicalIndicators.calculate_sma(
            close, config.SMA_SHORT
        )
        df['SMA_長'] = TechnicalIndicators.calculate_sma(
            close, config.SMA_LONG
        )
        
        # EMA
        df['EMA_短'] = TechnicalIndicators.calculate_ema(
            close, config.EMA_SHORT
        )
        df['EMA_長'] = TechnicalIndicators.calculate_ema(
            close, config.EMA_LONG
        )
        
        # RSI
        df['RSI'] = TechnicalIndicators.calculate_rsi(
            close, config.RSI_PERIOD
        )
        
        # MACD
        macd_data = TechnicalIndicators.calculate_macd(
            close,
            config.MACD_FAST,
            config.MACD_SLOW,
            config.MACD_SIGNAL
        )
        df['MACD'] = macd_data['macd']
        df['MACD_Signal'] = macd_data['signal']
        df['MACD_Histogram'] = macd_data['histogram']
        
        return df


# テスト用
if __name__ == "__main__":
    from core.price_fetcher import PriceFetcher
    
    fetcher = PriceFetcher()
    df = fetcher.fetch_latest_bars(num_bars=50, interval="1h")
    
    if df is not None:
        df = TechnicalIndicators.analyze(df)
        
        print("=" * 80)
        print("テクニカル指標計算結果")
        print("=" * 80)
        print(df[['終値', 'SMA_短', 'SMA_長', 'RSI', 'MACD']].tail(10))

