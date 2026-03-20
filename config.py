"""
FXsupporter 設定ファイル
"""
import os
from dotenv import load_dotenv

load_dotenv()

CURRENCY_PAIR = "GBPJPY=X"
CURRENCY_PAIR_DISPLAY = "GBP/JPY"

RISK_PERCENTAGE = 3.0
LOT_SIZE = 1000

SMA_SHORT = 5
SMA_LONG = 25
EMA_SHORT = 12
EMA_LONG = 26
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")

DB_PATH = "fxsupporter.db"

DEBUG = os.getenv("DEBUG", "False") == "True"

