"""
LINE Notify 通知モジュール
LINEにアラート通知を送信
"""
import requests
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

class LineNotifier:
    """LINE通知を送信するクラス"""
    
    def __init__(self, token=None):
        """
        Args:
            token (str): LINE Notify トークン
        """
        self.token = token or config.LINE_NOTIFY_TOKEN
        self.endpoint = "https://notify-api.line.me/api/notify"
    
    def send(self, message):
        """
        LINE Notifyでメッセージを送信
        
        Args:
            message (str): 送信するメッセージ
        
        Returns:
            dict: {
                'success': True/False,
                'status_code': ステータスコード,
                'response': レスポンス内容
            }
        """
        if not self.token:
            return {
                'success': False,
                'status_code': 0,
                'response': 'LINE Notifyトークンが設定されていません',
                'message': 'トークンを .env ファイルで設定してください'
            }
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'message': message}
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                data=data,
                timeout=10
            )
            
            success = response.status_code == 200
            
            return {
                'success': success,
                'status_code': response.status_code,
                'response': response.text,
                'message': message
            }
        except Exception as e:
            return {
                'success': False,
                'status_code': 0,
                'response': str(e),
                'error': 'リクエストに失敗しました'
            }
    
    def send_signal(self, strategy_name, signal, confidence, reason, 
                   current_price):
        """
        トレードシグナル通知を送信
        
        Args:
            strategy_name (str): 戦略名
            signal (str): 'BUY' or 'SELL'
            confidence (float): 信頼度
            reason (str): 理由
            current_price (float): 現在価格
        
        Returns:
            dict: 送信結果
        """
        emoji = "🟢" if signal == "BUY" else "🔴"
        
        message = f"""{emoji} 【{signal}シグナル】
戦略: {strategy_name}
現在価格: ¥{current_price:.2f}
信頼度: {confidence:.0%}
理由: {reason}"""
        
        return self.send(message)
    
    def send_entry(self, entry_price, lots, stop_loss, target_price):
        """
        エントリー通知を送信
        
        Args:
            entry_price (float): エントリー価格
            lots (float): ロット数
            stop_loss (float): ストップロス
            target_price (float): 目標利確レート
        
        Returns:
            dict: 送信結果
        """
        message = f"""📍 【エントリー】
エントリー価格: ¥{entry_price:.2f}
ロット数: {lots}
ストップロス: ¥{stop_loss:.2f}
目標レート: ¥{target_price:.2f}"""
        
        return self.send(message)
    
    def send_exit(self, exit_type, exit_price, entry_price, pnl):
        """
        決済通知を送信（利確・損切り）
        
        Args:
            exit_type (str): 'PROFIT' or 'LOSS'
            exit_price (float): 決済レート
            entry_price (float): エントリー価格
            pnl (float): 損益（円）
        
        Returns:
            dict: 送信結果
        """
        emoji = "✅" if exit_type == "PROFIT" else "❌"
        status_text = "利確" if exit_type == "PROFIT" else "損切り"
        
        message = f"""{emoji} 【{status_text}】
決済レート: ¥{exit_price:.2f}
エントリー: ¥{entry_price:.2f}
損益: ¥{pnl:+,.0f}"""
        
        return self.send(message)
    
    def send_alert(self, alert_type, message_detail):
        """
        アラート通知を送信
        
        Args:
            alert_type (str): アラートの種類（'WARNING', 'ERROR' など）
            message_detail (str): 詳細メッセージ
        
        Returns:
            dict: 送信結果
        """
        emoji = "⚠️" if alert_type == "WARNING" else "🚨"
        
        message = f"""{emoji} 【{alert_type}】
{message_detail}"""
        
        return self.send(message)


# テスト用
if __name__ == "__main__":
    notifier = LineNotifier()
    
    print("=" * 70)
    print("LINE Notify テスト")
    print("=" * 70)
    
    # テスト1: シグナル通知
    print("\n【テスト1】シグナル通知")
    result1 = notifier.send_signal(
        strategy_name="SMA Cross",
        signal="BUY",
        confidence=0.7,
        reason="短期SMAが長期SMAを上抜け",
        current_price=170.50
    )
    print(f"送信結果: {'成功' if result1['success'] else '失敗'}")
    if not result1['success']:
        print(f"  原因: {result1.get('message', result1.get('response', '不明'))}")
    
    # テスト2: エントリー通知
    print("\n【テスト2】エントリー通知")
    result2 = notifier.send_entry(
        entry_price=170.50,
        lots=1.0,
        stop_loss=169.50,
        target_price=173.00
    )
    print(f"送信結果: {'成功' if result2['success'] else '失敗'}")
    
    # テスト3: 利確通知
    print("\n【テスト3】利確通知")
    result3 = notifier.send_exit(
        exit_type="PROFIT",
        exit_price=173.00,
        entry_price=170.50,
        pnl=50000
    )
    print(f"送信結果: {'成功' if result3['success'] else '失敗'}")
    
    # テスト4: アラート
    print("\n【テスト4】アラート通知")
    result4 = notifier.send_alert(
        alert_type="WARNING",
        message_detail="含み損が3%ルール近くに達しています"
    )
    print(f"送信結果: {'成功' if result4['success'] else '失敗'}")

