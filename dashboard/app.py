"""
FXsupporter Streamlit ダッシュボード
リアルタイム価格・シグナル・リスク管理を表示
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.price_fetcher import PriceFetcher
from indicators.technical import TechnicalIndicators
from strategies.sma_cross import SMAcrossStrategy
from core.risk_manager import RiskManager
from core.profit_calculator import ProfitCalculator
from notifications.line_notify import LineNotifier
import config

# ページ設定
st.set_page_config(
    page_title="FXsupporter",
    page_icon="💱",
    layout="wide"
)

# タイトル
st.title("💱 FX運用サポートアプリ - GBP/JPY")
st.markdown("初心者向けのトレードサポートツール")

# ===== サイドバー設定 =====
st.sidebar.header("⚙️ 設定")

# 口座資金設定
account_balance = st.sidebar.number_input(
    "口座資金（円）",
    value=1000000,
    min_value=100000,
    step=100000,
    help="トレードに使用する資金"
)

# ローソク足の期間選択
interval = st.sidebar.selectbox(
    "ローソク足の間隔",
    ["1m", "5m", "15m", "1h", "1d"],
    index=3,
    help="チャートの時間足"
)

# 表示本数
num_bars = st.sidebar.slider(
    "表示するローソク足の本数",
    min_value=20,
    max_value=200,
    value=50,
    step=10
)

# ===== メイン画面 =====

# 1. 現在の価格
st.header("📊 現在のGBP/JPY価格")

fetcher = PriceFetcher()
current = fetcher.fetch_current_price()

if current:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="現在値",
            value=f"¥{current['price']:.2f}",
            delta="リアルタイム更新"
        )
    
    with col2:
        st.metric(
            label="更新時刻",
            value=current['timestamp'].strftime("%H:%M:%S")
        )
    
    with col3:
        st.metric(
            label="許容リスク（3%）",
            value=f"¥{account_balance * 0.03:,.0f}"
        )
else:
    st.error("価格データの取得に失敗しました")
    st.stop()

st.divider()

# 2. テクニカル分析
st.header("📈 テクニカル分析")

# データ取得
df = fetcher.fetch_latest_bars(num_bars=num_bars, interval=interval)

if df is not None:
    # 指標計算
    df = TechnicalIndicators.analyze(df)
    
    # 最新のテクニカル値を表示
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="SMA（短期5）",
            value=f"¥{latest['SMA_短']:.2f}" if pd.notna(latest['SMA_短']) else "計算中"
        )
    
    with col2:
        st.metric(
            label="SMA（長期25）",
            value=f"¥{latest['SMA_長']:.2f}" if pd.notna(latest['SMA_長']) else "計算中"
        )
    
    with col3:
        rsi_value = latest['RSI']
        rsi_status = "買われすぎ" if rsi_value > 70 else "売られすぎ" if rsi_value < 30 else "中立"
        st.metric(
            label="RSI（14）",
            value=f"{rsi_value:.1f}" if pd.notna(rsi_value) else "計算中",
            delta=rsi_status
        )
    
    with col4:
        macd_value = latest['MACD']
        macd_status = "強気" if macd_value > 0 else "弱気" if macd_value < 0 else "中立"
        st.metric(
            label="MACD",
            value=f"{macd_value:.4f}" if pd.notna(macd_value) else "計算中",
            delta=macd_status
        )
    
    st.divider()
    
    # 3. トレードシグナル
    st.header("🎯 トレードシグナル")
    
    strategy = SMAcrossStrategy()
    signal_result = strategy.get_latest_signal(df)
    
    # シグナル表示
    signal = signal_result['signal']
    confidence = signal_result['confidence']
    reason = signal_result['reason']
    
    if signal == "BUY":
        st.success(f"🟢 **BUYシグナル**", icon="✅")
    elif signal == "SELL":
        st.error(f"🔴 **SELLシグナル**", icon="⛔")
    else:
        st.info(f"⚪ **HOLDシグナル**", icon="⏸️")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="信頼度", value=f"{confidence:.0%}")
    with col2:
        st.metric(label="戦略", value="SMA Cross")
    
    st.write(f"**理由:** {reason}")
    
    st.divider()
    
    # 4. リスク管理
    st.header("🛡️ リスク管理（3%ルール）")
    
    rm = RiskManager(account_balance=account_balance)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ロット数計算")
        entry_price = st.number_input(
            "エントリー価格（円）",
            value=current['price'],
            min_value=100.0,
            max_value=500.0,
            step=0.01
        )
        
        stop_loss = st.number_input(
            "ストップロス価格（円）",
            value=current['price'] - 1.0,
            min_value=100.0,
            max_value=500.0,
            step=0.01
        )
        
        lot_result = rm.calculate_lot_size(entry_price, stop_loss)
        
        st.metric(
            label="推奨ロット数",
            value=f"{lot_result['lots']:.2f} Lot"
        )
        st.metric(
            label="取引通貨数",
            value=f"{lot_result['units']:,} GBP"
        )
        st.metric(
            label="リスク額（3%）",
            value=f"¥{lot_result['risk_amount']:,.0f}"
        )
    
    with col2:
        st.subheader("利確レート計算")
        target_profit = st.number_input(
            "目標利益額（円）",
            value=50000,
            min_value=10000,
            step=10000
        )
        
        pc = ProfitCalculator()
        profit_result = pc.calculate_target_rate(
            entry_price=entry_price,
            lots=lot_result['lots'],
            target_profit_yen=target_profit,
            spread=0.01
        )
        
        st.metric(
            label="目標利確レート",
            value=f"¥{profit_result['target_price']:.2f}"
        )
        st.metric(
            label="必要なpip数",
            value=f"{profit_result['pips_needed']:.2f}"
        )
        st.metric(
            label="予想利益",
            value=f"¥{profit_result['net_profit']:,.0f}"
        )
        
        # リスクリワード比
        rr = pc.calculate_risk_reward_ratio(
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=profit_result['target_price']
        )
        st.metric(
            label="RR比",
            value=rr['ratio_text'],
            delta=rr['status']
        )
    
    st.divider()
    
    # 5. チャート表示
    st.header("📉 チャート")
    
    # 終値のチャート
    chart_data = df[['終値', 'SMA_短', 'SMA_長']].copy()
    chart_data.columns = ['終値', 'SMA(5)', 'SMA(25)']
    
    st.line_chart(chart_data)
    
    st.divider()
    
    # 6. 詳細データテーブル
    st.header("📋 詳細データ")
    
    if st.checkbox("詳細なテクニカル指標を表示"):
        display_df = df[['終値', 'SMA_短', 'SMA_長', 'EMA_短', 'EMA_長', 'RSI', 'MACD']].tail(10).copy()
        display_df = display_df.round(4)
        st.dataframe(display_df, use_container_width=True)
    
    st.divider()
    
    # 7. LINE通知テスト
    st.header("📱 通知設定")
    
    if st.button("LINE通知をテスト送信"):
        notifier = LineNotifier()
        result = notifier.send_signal(
            strategy_name="SMA Cross",
            signal=signal,
            confidence=confidence,
            reason=reason,
            current_price=current['price']
        )
        
        if result['success']:
            st.success("✅ LINE通知を送信しました！")
        else:
            st.warning(f"⚠️ 通知送信に失敗しました: {result.get('message', 'LINE Notifyトークンを設定してください')}")

else:
    st.error("データの取得に失敗しました")

# フッター
st.divider()
st.markdown("""
---
**🔔 注意:**
- このアプリは初心者向けのサポートツールです
- 実際の取引は自己判断で行ってください
- リスク管理を厳密に守ってください
- テクニカル分析は参考情報です

**📞 お問い合わせ:** 松井証券サポート
""")

