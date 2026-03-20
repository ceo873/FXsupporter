"""
利益目標からの逆算機能
目標利益額から必要な利確レートを計算
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

class ProfitCalculator:
    """利益計算・逆算を行うクラス"""
    
    def __init__(self):
        pass
    
    def calculate_target_rate(self, entry_price, lots, target_profit_yen, 
                             spread=0.01, commission=0):
        """
        目標利益額から利確レートを逆算
        
        Args:
            entry_price (float): エントリー価格（円）
            lots (float): ロット数（1 Lot = 1000 GBP）
            target_profit_yen (float): 目標利益額（円）
            spread (float): スプレッド（円）- デフォルト 0.01
            commission (float): 手数料（円）- デフォルト 0
        
        Returns:
            dict: {
                'target_price': 目標利確価格,
                'pips_needed': 必要なpip数,
                'gross_profit': 粗利益,
                'net_profit': 手数料差引後の利益,
                'status': ステータス
            }
        """
        pip_value = 0.01  # 1 pip = 0.01円
        units = lots * 1000  # ロット数を通貨数に変換
        
        if units == 0:
            return {
                'target_price': 0,
                'pips_needed': 0,
                'gross_profit': 0,
                'net_profit': 0,
                'status': 'error',
                'error_message': 'ロット数が0です'
            }
        
        # スプレッド分を考慮（買いの場合、スプレッド分上乗せが必要）
        effective_entry = entry_price + spread
        
        # 必要な利益（スプレッド + 手数料分も含める）
        total_cost = spread + commission
        required_profit = target_profit_yen + total_cost
        
        # 必要なpip数を計算
        # 利益 = units × pip数 × pip_value
        # pip数 = 利益 / (units × pip_value)
        pips_needed = required_profit / (units * pip_value)
        
        # 利確レート = エントリー + (pips × pip_value)
        target_price = effective_entry + (pips_needed * pip_value)
        
        # 検証用：逆算した利益を計算
        gross_profit = (units * pips_needed * pip_value) - spread
        net_profit = gross_profit - commission
        
        return {
            'entry_price': round(entry_price, 2),
            'target_price': round(target_price, 2),
            'pips_needed': round(pips_needed, 2),
            'units': int(units),
            'lots': lots,
            'gross_profit': round(gross_profit, 0),
            'net_profit': round(net_profit, 0),
            'target_profit_yen': target_profit_yen,
            'spread': spread,
            'commission': commission,
            'status': 'ok'
        }
    
    def calculate_breakeven_rate(self, entry_price, spread=0.01, commission=0):
        """
        損益分岐点レートを計算
        
        Args:
            entry_price (float): エントリー価格（円）
            spread (float): スプレッド（円）
            commission (float): 手数料（円）
        
        Returns:
            dict: 損益分岐点情報
        """
        total_cost = (spread + commission) / 1000  # 通貨あたりのコスト
        breakeven_rate = entry_price + total_cost
        
        return {
            'entry_price': round(entry_price, 2),
            'breakeven_rate': round(breakeven_rate, 4),
            'pips_to_breakeven': round(total_cost / 0.01, 2),
            'spread': spread,
            'commission': commission
        }
    
    def calculate_multiple_targets(self, entry_price, lots, profit_amounts, 
                                   spread=0.01, commission=0):
        """
        複数の利益目標に対応する利確レートをまとめて計算
        
        Args:
            entry_price (float): エントリー価格
            lots (float): ロット数
            profit_amounts (list): 利益目標額のリスト [10000, 30000, 50000]
        
        Returns:
            list: 複数の利確レート情報
        """
        results = []
        for profit in profit_amounts:
            result = self.calculate_target_rate(
                entry_price, lots, profit, spread, commission
            )
            results.append(result)
        
        return results
    
    def calculate_risk_reward_ratio(self, entry_price, stop_loss, target_price):
        """
        リスクリワード比を計算
        高いほど良い取引（例：1:3 = 1円損する可能性で3円稼ぐ可能性）
        
        Args:
            entry_price (float): エントリー価格
            stop_loss (float): ストップロス価格
            target_price (float): 目標利確レート
        
        Returns:
            dict: リスクリワード比情報
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        
        if risk == 0:
            return {
                'risk_pips': 0,
                'reward_pips': 0,
                'ratio': 0,
                'status': 'error'
            }
        
        ratio = reward / risk
        
        return {
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'target_price': round(target_price, 2),
            'risk_pips': round(risk / 0.01, 2),
            'reward_pips': round(reward / 0.01, 2),
            'ratio': round(ratio, 2),
            'ratio_text': f'1: {ratio:.2f}',
            'status': '✅ 良好' if ratio >= 1.5 else '⚠️  確認推奨'
        }


# テスト用
if __name__ == "__main__":
    calc = ProfitCalculator()
    
    print("=" * 80)
    print("利益計算ツール テスト")
    print("=" * 80)
    
    # テストケース1: 目標利益 50,000円
    print("\n【テストケース1】エントリー170円、目標利益¥50,000")
    result1 = calc.calculate_target_rate(
        entry_price=170.0,
        lots=1.0,
        target_profit_yen=50000,
        spread=0.01
    )
    print(f"  エントリー: ¥{result1['entry_price']}")
    print(f"  目標利確レート: ¥{result1['target_price']}")
    print(f"  必要なpip数: {result1['pips_needed']}")
    print(f"  粗利益: ¥{result1['gross_profit']:,.0f}")
    print(f"  手数料差引後: ¥{result1['net_profit']:,.0f}")
    
    # テストケース2: 複数目標
    print("\n【テストケース2】複数の利益目標")
    results = calc.calculate_multiple_targets(
        entry_price=170.0,
        lots=1.0,
        profit_amounts=[30000, 50000, 100000]
    )
    for r in results:
        print(f"  目標¥{r['target_profit_yen']:,} → レート: ¥{r['target_price']}")
    
    # テストケース3: リスクリワード比
    print("\n【テストケース3】リスクリワード比")
    rr = calc.calculate_risk_reward_ratio(
        entry_price=170.0,
        stop_loss=169.0,
        target_price=result1['target_price']
    )
    print(f"  リスク: {rr['risk_pips']} pips")
    print(f"  リワード: {rr['reward_pips']} pips")
    print(f"  比率: {rr['ratio_text']}")
    print(f"  評価: {rr['status']}")

