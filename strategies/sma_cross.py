"""
SMA（移動平均線）クロス戦略
短期SMAが長期SMAを上抜けたらBUY、下抜けたらSELL
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base import BaseStrategy

class SMAcrossStrategy(BaseStrategy):
    """SMAクロス戦略"""
    
    def __init__(self):
        super().__init__(name="SMA Cross")
    
    def generate_signal(self, df):
        """
        SMAクロスシグナルを生成
        
        Args:
            df (DataFrame): テクニカル指標を含むOHLCデータ
        
        Returns:
            dict: シグナル情報
        """
        if df is None or len(df) < 2:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': 'データが不足しています'
            }
        
        # 最新と1つ前のデータを取得
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        sma_short = current['SMA_短']
        sma_long = current['SMA_長']
        prev_sma_short = previous['SMA_短']
        prev_sma_long = previous['SMA_長']
        
        # NaN チェック
        if pd.isna(sma_short) or pd.isna(sma_long):
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': 'SMAの計算中'
            }
        
        # シグナル判定
        # BUY: 短期SMA > 長期SMA かつ 前のロウソク足では短期SMA <= 長期SMA
        if sma_short > sma_long and prev_sma_short <= prev_sma_long:
            return {
                'signal': 'BUY',
                'confidence': 0.7,
                'reason': f'短期SMA({sma_short:.2f}) が長期SMA({sma_long:.2f}) を上抜け'
            }
        
        # SELL: 短期SMA < 長期SMA かつ 前のロウソク足では短期SMA >= 長期SMA
        elif sma_short < sma_long and prev_sma_short >= prev_sma_long:
            return {
                'signal': 'SELL',
                'confidence': 0.7,
                'reason': f'短期SMA({sma_short:.2f}) が長期SMA({sma_long:.2f}) を下抜け'
            }
        
        # HOLD
        else:
            return {
                'signal': 'HOLD',
                'confidence': 0.5,
                'reason': f'SMAがクロスしていません'
            }


import pandas as pd

# テスト用
if __name__ == "__main__":
    from core.price_fetcher import PriceFetcher
    from indicators.technical import TechnicalIndicators
    
    fetcher = PriceFetcher()
    df = fetcher.fetch_latest_bars(num_bars=50, interval="1h")
    
    if df is not None:
        df = TechnicalIndicators.analyze(df)
        
        strategy = SMAcrossStrategy()
        signal = strategy.get_latest_signal(df)
        
        print("=" * 70)
        print("SMA Cross Strategy テスト")
        print("=" * 70)
        print(f"戦略: {signal['strategy']}")
        print(f"シグナル: {signal['signal']}")
        print(f"信頼度: {signal['confidence']:.0%}")
        print(f"理由: {signal['reason']}")

