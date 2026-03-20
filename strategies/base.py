"""
戦略プラグインの基底クラス
すべての戦略はこれを継承して実装
"""
from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """戦略の基底クラス"""
    
    def __init__(self, name):
        """
        Args:
            name (str): 戦略の名前
        """
        self.name = name
        self.signal = None  # 'BUY', 'SELL', 'HOLD'
        self.confidence = 0.0  # 信頼度（0-1.0）
        self.reason = ""  # シグナルの理由
    
    @abstractmethod
    def generate_signal(self, df):
        """
        シグナルを生成（各戦略で実装）
        
        Args:
            df (DataFrame): テクニカル指標を含むOHLCデータ
        
        Returns:
            dict: {
                'signal': 'BUY' or 'SELL' or 'HOLD',
                'confidence': 信頼度（0-1.0）,
                'reason': シグナルの理由
            }
        """
        pass
    
    def get_latest_signal(self, df):
        """
        最新のシグナルを取得
        
        Args:
            df (DataFrame): テクニカル指標データ
        
        Returns:
            dict: シグナル情報
        """
        result = self.generate_signal(df)
        
        self.signal = result['signal']
        self.confidence = result['confidence']
        self.reason = result['reason']
        
        return {
            'strategy': self.name,
            'signal': self.signal,
            'confidence': self.confidence,
            'reason': self.reason
        }

