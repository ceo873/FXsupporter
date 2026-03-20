"""
リスク管理モジュール
3%ルールに基づくロット計算と損切りストップ管理
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

class RiskManager:
    """リスク管理を行うクラス"""
    
    def __init__(self, account_balance):
        """
        Args:
            account_balance (float): 口座資金（円）
        """
        self.account_balance = account_balance
        self.risk_percentage = config.RISK_PERCENTAGE  # 3%
        self.lot_size = config.LOT_SIZE  # 1ロット=1000通貨
    
    def max_risk_amount(self):
        """
        口座に対して許容できる最大損失額を計算
        
        Returns:
            float: 最大損失額（円）
        """
        return self.account_balance * (self.risk_percentage / 100)
    
    def calculate_lot_size(self, entry_price, stop_loss_price):
        """
        エントリー価格とストップロス価格から、
        3%ルールを守るためのロット数を計算
        
        Args:
            entry_price (float): エントリー価格（円）
            stop_loss_price (float): ストップロス価格（円）
        
        Returns:
            dict: {
                'lots': ロット数,
                'units': 取引通貨数,
                'risk_amount': リスク額（円）,
                'profit_per_pip': 1pip当たりの利益(円)
            }
        """
        # 1pip = 0.01円 と仮定
        pip_value = 0.01
        
        # エントリー～ストップロスの差分（pip数）
        pips = abs(entry_price - stop_loss_price) / pip_value
        
        if pips == 0:
            return {
                'lots': 0,
                'units': 0,
                'risk_amount': 0,
                'profit_per_pip': 0,
                'status': 'error'
            }
        
        # 許容リスク額
        max_risk = self.max_risk_amount()
        
        # 1pipあたりのリスク額 = 取引量（円）× pip_value
        # リスク額 = 1pipあたりのリスク額 × pip数
        # 取引金額（円）= リスク額 / pip数
        
        units = int((max_risk / pips) / pip_value)
        lots = units / self.lot_size
        
        # 1 Lot(1000通貨) の利益 = 1pip × 1000 × 0.01円 = 10円
        profit_per_pip = units * pip_value
        
        return {
            'lots': round(lots, 2),
            'units': units,
            'risk_amount': round(max_risk, 2),
            'profit_per_pip': round(profit_per_pip, 2),
            'status': 'ok'
        }
    
    def calculate_take_profit(self, entry_price, lots, target_profit_yen):
        """
        目標利益額から利確レートを逆算
        
        Args:
            entry_price (float): エントリー価格（円）
            lots (float): ロット数
            target_profit_yen (float): 目標利益額（円）
        
        Returns:
            dict: {
                'target_price': 目標利確価格,
                'pips': 必要なpip数,
                'status': ステータス
            }
        """
        pip_value = 0.01
        units = lots * self.lot_size
        
        if units == 0:
            return {
                'target_price': 0,
                'pips': 0,
                'status': 'error'
            }
        
        # 必要なpip数 = 目標利益 / (units × pip_value)
        required_pips = target_profit_yen / (units * pip_value)
        
        # 利確レート（買いの場合はエントリーより上）
        target_price = entry_price + (required_pips * pip_value)
        
        return {
            'target_price': round(target_price, 2),
            'pips': round(required_pips, 2),
            'required_profit_yen': round(target_profit_yen, 2),
            'status': 'ok'
        }
    
    def validate_position(self, entry_price, stop_loss, current_price):
        """
        現在のポジションが3%ルール内か検証
        
        Args:
            entry_price (float): エントリー価格
            stop_loss (float): ストップロス価格
            current_price (float): 現在価格
        
        Returns:
            dict: ポジション情報と警告
        """
        unrealized_loss = abs(current_price - entry_price)
        max_risk = self.max_risk_amount()
        
        # 1pips = 0.01円で取引量に応じた損失を計算（簡易版）
        pip_value = 0.01
        pips_loss = unrealized_loss / pip_value
        
        # 1pipあたりの平均的な利益を100円と仮定（取引量に応じて調整）
        estimated_loss = pips_loss * 100  # 粗い推定
        
        is_safe = estimated_loss <= max_risk
        
        return {
            'entry_price': entry_price,
            'current_price': current_price,
            'stop_loss': stop_loss,
            'unrealized_loss': round(unrealized_loss, 2),
            'max_risk_allowed': round(max_risk, 2),
            'is_within_risk': is_safe,
            'status': '✅ 安全' if is_safe else '🚨 注意'
        }


# テスト用
if __name__ == "__main__":
    # 口座資金: 100万円
    rm = RiskManager(account_balance=1000000)
    
    print("=" * 70)
    print("リスク管理テスト")
    print("=" * 70)
    print(f"口座資金: ¥{rm.account_balance:,}")
    print(f"許容リスク（3%）: ¥{rm.max_risk_amount():,.0f}\n")
    
    # ケース1: エントリー価格 170円、ストップロス 169円
    print("【ケース1】エントリー170円、ストップロス169円")
    result1 = rm.calculate_lot_size(170.0, 169.0)
    print(f"  推奨ロット数: {result1['lots']}")
    print(f"  取引通貨数: {result1['units']:,} GBP")
    print(f"  リスク額: ¥{result1['risk_amount']:,.0f}")
    print(f"  1pip当たりの利益: ¥{result1['profit_per_pip']:.0f}\n")
    
    # ケース2: 目標利益 5万円で利確レート計算
    print("【ケース2】目標利益 ¥50,000 の利確レート計算")
    result2 = rm.calculate_take_profit(
        entry_price=170.0,
        lots=result1['lots'],
        target_profit_yen=50000
    )
    print(f"  目標利確レート: ¥{result2['target_price']}")
    print(f"  必要なpip数: {result2['pips']}\n")
    
    # ケース3: ポジション検証
    print("【ケース3】現在のポジション検証")
    result3 = rm.validate_position(170.0, 169.0, 169.5)
    print(f"  現在価格: ¥{result3['current_price']}")
    print(f"  含み損: ¥{result3['unrealized_loss']:.2f}")
    print(f"  安全性: {result3['status']}")

