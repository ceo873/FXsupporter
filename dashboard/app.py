"""
FXsupporter - 北欧ミニマルデザイン版
シンプルで洗練されたトレードサポートダッシュボード
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    /* グローバル設定 */
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    
    /* ヘッダー */
    h1 { 
        color: #1E88E5;
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #1A1A1A;
        font-size: 1.5rem;
        font-weight: 400;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E0E0E0;
        padding-bottom: 0.5rem;
    }
    
    /* メトリクス */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* テキスト */
    p { color: #424242; line-height: 1.6; }
    
    /* ボタン */
    button {
        background-color: #1E88E5 !important;
        color: white !important;
        font-weight: 500;
        border-radius: 6px !important;
        border: none !important;
    }
    
    button:hover {
        background-color: #1565C0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ===== メイン画面 =====

# タイトル
st.markdown("# 💱 FXsupporter")
st.markdown("*初心者向けのシンプルで洗練されたトレードサポートツール*")

st.divider()

# ===== サイドバー設定 =====
with st.sidebar:
    st.markdown("## ⚙️ 設定")
    
    account_balance = st.number_input(
        "口座資金（円）",
        value=1000000,
        min_value=100000,
        step=100000,
        help="トレードに使用する資金額"
    )
    
    interval = st.selectbox(
        "ローソク足の間隔",
        ["1m", "5m", "15m", "1h", "1d"],
        index=3
    )
    
    num_bars = st.slider(
        "表示本数",
        min_value=20,
        max_value=200,
        value=50,
        step=10
    )

# ===== コンテンツエリア =====

# 1. 現在の価格
fetcher = PriceFetcher()
current = fetcher.fetch_current_price()

if current:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "現在値",
            f"¥{current['price']:.2f}",
            "リアルタイム"
        )
    
    with col2:
        st.metric(
            "更新時刻",
            current['timestamp'].strftime("%H:%M:%S")
        )
    
    with col3:
        st.metric(
            "許容リスク（3%）",
            f"¥{account_balance * 0.03:,.0f}"
        )
    
    st.divider()
    
    # 2. データ取得と分析
    df = fetcher.fetch_latest_bars(num_bars=num_bars, interval=interval)
    
    if df is not None:
        df = TechnicalIndicators.analyze(df)
        latest = df.iloc[-1]
        
        # テクニカル指標
        st.markdown("## 📈 テクニカル指標")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "SMA（短期）",
                f"¥{latest['SMA_短']:.2f}" if pd.notna(latest['SMA_短']) else "計算中"
            )
        
        with col2:
            st.metric(
                "SMA（長期）",
                f"¥{latest['SMA_長']:.2f}" if pd.notna(latest['SMA_長']) else "計算中"
            )
        
        with col3:
            rsi = latest['RSI']
            st.metric(
                "RSI",
                f"{rsi:.1f}" if pd.notna(rsi) else "計算中"
            )
        
        with col4:
            macd = latest['MACD']
            st.metric(
                "MACD",
                f"{macd:.4f}" if pd.notna(macd) else "計算中"
            )
        
        st.divider()
        
        # 3. トレードシグナル
        st.markdown("## 🎯 トレードシグナル")
        
        strategy = SMAcrossStrategy()
        signal_result = strategy.get_latest_signal(df)
        signal = signal_result['signal']
        confidence = signal_result['confidence']
        reason = signal_result['reason']
        
        # シグナル表示
        if signal == "BUY":
            st.success("🟢 **BUY シグナル**", icon="✅")
        elif signal == "SELL":
            st.error("🔴 **SELL シグナル**", icon="⛔")
        else:
            st.info("⚪ **HOLD（シグナルなし）**", icon="⏸️")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("信頼度", f"{confidence:.0%}")
        with col2:
            st.metric("戦略", "SMA Cross")
        
        st.write(f"**根拠:** {reason}")
        
        st.divider()
        
        # 4. リスク管理とロット計算
        st.markdown("## 🛡️ リスク管理")
        
        rm = RiskManager(account_balance=account_balance)
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("ロット数計算")
            
            entry_price = st.number_input(
                "エントリー価格",
                value=current['price'],
                min_value=100.0,
                max_value=500.0,
                step=0.01,
                key="entry"
            )
            
            stop_loss = st.number_input(
                "ストップロス価格",
                value=current['price'] - 1.0,
                min_value=100.0,
                max_value=500.0,
                step=0.01,
                key="sl"
            )
            
            lot_result = rm.calculate_lot_size(entry_price, stop_loss)
            
            st.metric("推奨ロット数", f"{lot_result['lots']:.2f}")
            st.metric("取引通貨数", f"{lot_result['units']:,} GBP")
            st.metric("リスク額", f"¥{lot_result['risk_amount']:,.0f}")
        
        with col_right:
            st.subheader("利確レート計算")
            
            target_profit = st.number_input(
                "目標利益",
                value=50000,
                min_value=10000,
                step=10000,
                key="profit"
            )
            
            pc = ProfitCalculator()
            profit_result = pc.calculate_target_rate(
                entry_price=entry_price,
                lots=lot_result['lots'],
                target_profit_yen=target_profit,
                spread=0.01
            )
            
            st.metric("目標レート", f"¥{profit_result['target_price']:.2f}")
            st.metric("必要pips", f"{profit_result['pips_needed']:.2f}")
            st.metric("予想利益", f"¥{profit_result['net_profit']:,.0f}")
            
            rr = pc.calculate_risk_reward_ratio(
                entry_price=entry_price,
                stop_loss=stop_loss,
                target_price=profit_result['target_price']
            )
            st.metric("RR比", rr['ratio_text'])
        
        st.divider()
        
        # 5. チャート
        st.markdown("## 📊 チャート")
        
        chart_data = df[['終値', 'SMA_短', 'SMA_長']].copy()
        chart_data.columns = ['終値', 'SMA(5)', 'SMA(25)']
        st.line_chart(chart_data, use_container_width=True)
        
        st.divider()
        
        # 6. 詳細データ
        st.markdown("## 📋 詳細データ")
        
        if st.checkbox("詳細なテクニカル指標を表示"):
            display_df = df[['終値', 'SMA_短', 'SMA_長', 'RSI', 'MACD']].tail(10).copy()
            display_df = display_df.round(4)
            st.dataframe(display_df, use_container_width=True)
        
        st.divider()
        
        # 7. LINE通知
        st.markdown("## 📱 通知")
        
        if st.button("LINE通知をテスト送信", use_container_width=True):
            notifier = LineNotifier()
            result = notifier.send_signal(
                strategy_name="SMA Cross",
                signal=signal,
                confidence=confidence,
                reason=reason,
                current_price=current['price']
            )
            
            if result['success']:
                st.success("✅ LINE通知を送信しました")
            else:
                st.warning(f"LINE Notifyトークンを設定してください")

else:
    st.error("価格データの取得に失敗しました")

# フッター
st.divider()
st.markdown("""
---
### ℹ️ 使い方
1. **左側のサイドバー** で口座資金を設定
2. **テクニカル指標** でトレンドを確認
3. **トレードシグナル** でエントリーのタイミングを判定
4. **リスク管理** でロット数と利確レートを計算
5. **実際の取引は松井証券で手動実行**

### ⚠️ 重要
- このアプリは初心者向けのサポートツールです
- 実際の取引は自己判断で行ってください
- リスク管理を厳密に守ってください
""")

