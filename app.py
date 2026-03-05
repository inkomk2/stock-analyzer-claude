import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ─── ページ設定 ───────────────────────────────────────────────
st.set_page_config(
    page_title="日経225 スイングトレード分析ツール",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── カスタムCSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
}

.main { background: #0d1117; }

/* ヘッダー */
.tool-header {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.tool-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f0f6fc;
    letter-spacing: -0.5px;
}

.tool-subtitle {
    color: #8b949e;
    font-size: 0.85rem;
    margin-top: 4px;
}

/* スコアカード */
.rank-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
    cursor: pointer;
}

.rank-card:hover { border-color: #388bfd; }

.rank-card.gold { border-left: 4px solid #FFD700; }
.rank-card.silver { border-left: 4px solid #C0C0C0; }
.rank-card.bronze { border-left: 4px solid #CD7F32; }
.rank-card.normal { border-left: 4px solid #21262d; }

/* スコアバー */
.score-bar-bg {
    background: #21262d;
    border-radius: 4px;
    height: 6px;
    width: 100%;
    margin-top: 6px;
}

.score-bar-fill {
    height: 6px;
    border-radius: 4px;
    background: linear-gradient(90deg, #238636, #2ea043);
}

/* タグ */
.signal-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px;
}

.tag-buy { background: #1a4a1a; color: #3fb950; border: 1px solid #238636; }
.tag-rsi { background: #1a3a5c; color: #79c0ff; border: 1px solid #388bfd; }
.tag-macd { background: #3a1a5c; color: #d2a8ff; border: 1px solid #8957e5; }
.tag-vol { background: #3a2a1a; color: #ffa657; border: 1px solid #f0883e; }
.tag-bb { background: #3a1a1a; color: #ff7b72; border: 1px solid #f85149; }

/* 注文ボックス */
.order-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
}

.order-label { color: #8b949e; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; }
.order-value { color: #f0f6fc; font-weight: 600; font-size: 1rem; }
.order-entry { color: #79c0ff; }
.order-profit { color: #3fb950; }
.order-loss { color: #f85149; }

/* メトリクス */
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px 18px;
    text-align: center;
}

.metric-value { font-size: 1.6rem; font-weight: 700; color: #f0f6fc; }
.metric-label { font-size: 0.75rem; color: #8b949e; margin-top: 4px; }

/* ポートフォリオ */
.portfolio-row {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 8px;
}

.profit { color: #3fb950; }
.loss { color: #f85149; }
.neutral { color: #8b949e; }

/* ボタンスタイル */
.stButton > button {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Noto Sans JP', sans-serif !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2ea043, #3fb950) !important;
}

/* セクションヘッダー */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0f6fc;
    border-bottom: 2px solid #21262d;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* ステータスバッジ */
.badge-profit { background: #1a4a1a; color: #3fb950; padding: 2px 8px; border-radius: 4px; }
.badge-loss { background: #4a1a1a; color: #f85149; padding: 2px 8px; border-radius: 4px; }
.badge-hold { background: #21262d; color: #8b949e; padding: 2px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─── 日経225 銘柄リスト（主要銘柄） ──────────────────────────
NIKKEI225_TICKERS = {
    "7203": "トヨタ自動車", "9984": "ソフトバンクG", "6758": "ソニーグループ",
    "8306": "三菱UFJ FG", "9432": "日本電信電話", "6861": "キーエンス",
    "8035": "東京エレクトロン", "7974": "任天堂", "6367": "ダイキン工業",
    "4063": "信越化学工業", "6954": "ファナック", "7267": "本田技研工業",
    "8316": "三井住友FG", "9433": "KDDI", "4519": "中外製薬",
    "6501": "日立製作所", "8411": "みずほFG", "7751": "キヤノン",
    "2914": "日本たばこ産業", "4543": "テルモ", "3382": "セブン&アイHD",
    "6098": "リクルートHD", "7733": "オリンパス", "4568": "第一三共",
    "6503": "三菱電機", "5108": "ブリヂストン", "7832": "バンダイナムコ",
    "3659": "ネクソン", "9022": "東海旅客鉄道", "9020": "東日本旅客鉄道",
    "8802": "三菱地所", "8801": "三井不動産", "2502": "アサヒグループHD",
    "2503": "キリンHD", "4901": "富士フイルムHD", "6752": "パナソニックHD",
    "6902": "デンソー", "7011": "三菱重工業", "5401": "日本製鉄",
    "4452": "花王", "8309": "三井住友トラスト", "1925": "大和ハウス工業",
    "6301": "小松製作所", "7201": "日産自動車", "6702": "富士通",
    "4578": "大塚HD", "2801": "キッコーマン", "3105": "日清紡HD",
    "6273": "SMC", "4507": "塩野義製薬"
}

PORTFOLIO_FILE = "portfolio.json"

# ─── ポートフォリオ管理 ───────────────────────────────────────
def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 型を正規化（JSONからfloatで読み込まれる可能性があるためintに統一）
        data["account_capital"] = float(data.get("account_capital", 3000000))
        data["monthly_target"] = float(data.get("monthly_target", 200000))
        for pos in data.get("positions", []):
            pos["entry_price"] = float(pos.get("entry_price", 0))
            pos["units"] = int(pos.get("units", 0))
            pos["take_profit"] = float(pos.get("take_profit", 0))
            pos["stop_loss"] = float(pos.get("stop_loss", 0))
        return data
    return {"positions": [], "account_capital": 3000000.0, "monthly_target": 200000.0}

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)

# ─── データ取得 ───────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_stock_data(ticker_code, period="3mo"):
    try:
        ticker = yf.Ticker(f"{ticker_code}.T")
        df = ticker.history(period=period, interval="1d")
        if df.empty or len(df) < 20:
            return None
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return None

@st.cache_data(ttl=300)
def get_current_price(ticker_code):
    try:
        ticker = yf.Ticker(f"{ticker_code}.T")
        info = ticker.fast_info
        return info.last_price
    except:
        return None

# ─── テクニカル指標計算 ──────────────────────────────────────
def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def calc_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

def calc_bollinger(series, period=20, std=2):
    ma = series.rolling(window=period).mean()
    std_dev = series.rolling(window=period).std()
    upper = ma + std * std_dev
    lower = ma - std * std_dev
    return upper, ma, lower

# ─── 市場環境チェック ────────────────────────────────────────
@st.cache_data(ttl=1800)
def calc_market_environment():
    """
    日経225・TOPIX・VIXを取得してトレンド判定。
    戻り値: dict {
        phase, phase_label, phase_color,
        score_multiplier,   # 個別スコアへの乗数 0.6〜1.15
        score_adj,          # 個別スコアへの加減点 -20〜+10
        nk_price, nk_1d, nk_5d, nk_20d,
        nk_ma5, nk_ma20, nk_rsi,
        topix_1d, topix_5d,
        vix, vix_level,
        warnings, positives
    }
    """
    result = {
        "phase": "neutral", "phase_label": "中立", "phase_color": "#8b949e",
        "score_multiplier": 1.0, "score_adj": 0,
        "nk_price": None, "nk_1d": 0.0, "nk_5d": 0.0, "nk_20d": 0.0,
        "nk_ma5": None, "nk_ma20": None, "nk_rsi": 50.0,
        "topix_1d": 0.0, "topix_5d": 0.0,
        "vix": None, "vix_level": "normal",
        "warnings": [], "positives": []
    }
    try:
        # 日経225
        nk = yf.Ticker("^N225")
        nk_df = nk.history(period="3mo", interval="1d")
        if nk_df is not None and len(nk_df) >= 20:
            nk_close = nk_df['Close']
            result["nk_price"] = nk_close.iloc[-1]
            result["nk_1d"]  = (nk_close.iloc[-1] / nk_close.iloc[-2]  - 1) * 100
            result["nk_5d"]  = (nk_close.iloc[-1] / nk_close.iloc[-5]  - 1) * 100 if len(nk_close) >= 5  else 0
            result["nk_20d"] = (nk_close.iloc[-1] / nk_close.iloc[-20] - 1) * 100 if len(nk_close) >= 20 else 0
            result["nk_ma5"]  = nk_close.rolling(5).mean().iloc[-1]
            result["nk_ma20"] = nk_close.rolling(20).mean().iloc[-1]
            result["nk_rsi"]  = calc_rsi(nk_close).iloc[-1]

        # TOPIX (ETF: 1306.T)
        try:
            tp = yf.Ticker("1306.T")
            tp_df = tp.history(period="1mo", interval="1d")
            if tp_df is not None and len(tp_df) >= 5:
                tc = tp_df['Close']
                result["topix_1d"] = (tc.iloc[-1] / tc.iloc[-2] - 1) * 100
                result["topix_5d"] = (tc.iloc[-1] / tc.iloc[-5] - 1) * 100 if len(tc) >= 5 else 0
        except:
            pass

        # VIX（日本版: ^JNIV、取れなければ^VIX）
        for vix_sym in ["^JNIV", "^VIX"]:
            try:
                vx = yf.Ticker(vix_sym)
                vx_df = vx.history(period="5d", interval="1d")
                if vx_df is not None and not vx_df.empty:
                    result["vix"] = vx_df['Close'].iloc[-1]
                    break
            except:
                pass

    except Exception as e:
        pass

    # ── フェーズ判定ロジック ──
    nk_price = result["nk_price"]
    nk_ma5   = result["nk_ma5"]
    nk_ma20  = result["nk_ma20"]
    nk_rsi   = result["nk_rsi"]
    nk_1d    = result["nk_1d"]
    nk_5d    = result["nk_5d"]
    nk_20d   = result["nk_20d"]
    vix      = result["vix"]

    warnings  = []
    positives = []
    adj       = 0  # スコア加減点

    if nk_price and nk_ma5 and nk_ma20:
        # 強気シグナル
        if nk_price > nk_ma5 > nk_ma20:
            positives.append("日経がMA5>MA20の上昇配列")
            adj += 5
        elif nk_price > nk_ma20:
            positives.append("日経がMA20上で推移")
            adj += 2

        # 弱気シグナル
        if nk_price < nk_ma20:
            warnings.append("日経がMA20を下回っている（下降トレンド）")
            adj -= 10
        if nk_price < nk_ma5 and nk_ma5 < nk_ma20:
            warnings.append("日経がデッドクロス配列（MA5<MA20）")
            adj -= 8

        # RSI
        if nk_rsi > 70:
            warnings.append(f"日経RSI={nk_rsi:.0f}（買われすぎ・調整リスク）")
            adj -= 6
        elif nk_rsi < 30:
            warnings.append(f"日経RSI={nk_rsi:.0f}（売られすぎ・反発期待あるも荒れやすい）")
            adj -= 5
        elif 40 <= nk_rsi <= 60:
            positives.append(f"日経RSI={nk_rsi:.0f}（健全ゾーン）")
            adj += 3

    # 直近騰落
    if nk_5d < -3.0:
        warnings.append(f"日経5日で{nk_5d:.1f}%下落（急落局面）")
        adj -= 10
    elif nk_5d < -1.5:
        warnings.append(f"日経5日で{nk_5d:.1f}%下落（軟調）")
        adj -= 5
    elif nk_5d > 2.0:
        positives.append(f"日経5日で+{nk_5d:.1f}%上昇（強い地合い）")
        adj += 5

    if nk_20d < -5.0:
        warnings.append(f"日経20日で{nk_20d:.1f}%下落（中期調整中）")
        adj -= 8
    elif nk_20d > 4.0:
        positives.append(f"日経20日で+{nk_20d:.1f}%上昇（中期上昇トレンド）")
        adj += 4

    # TOPIX確認（日経と方向感が一致しているか）
    if result["topix_5d"] < -2.0 and nk_5d < -1.0:
        warnings.append("TOPIX・日経ともに軟調（広範な売り圧力）")
        adj -= 5
    elif result["topix_5d"] > 1.5 and nk_5d > 1.0:
        positives.append("TOPIX・日経ともに上昇（地合い良好）")
        adj += 3

    # VIX
    if vix:
        result["vix_level"] = "high" if vix > 25 else ("elevated" if vix > 20 else "normal")
        if vix > 25:
            warnings.append(f"VIX={vix:.1f}（高水準・市場の恐怖感が強い）")
            adj -= 12
        elif vix > 20:
            warnings.append(f"VIX={vix:.1f}（やや高め・ボラティリティ注意）")
            adj -= 5
        else:
            positives.append(f"VIX={vix:.1f}（低水準・安定した市場環境）")
            adj += 3

    # ── フェーズ決定 ──
    total_signals = len(positives) - len(warnings)
    if adj >= 10 and not warnings:
        phase, label, color, mult = "bull",      "🟢 強気",    "#3fb950", 1.15
    elif adj >= 4:
        phase, label, color, mult = "mild_bull", "🟡 やや強気", "#ffa657", 1.05
    elif adj >= -3:
        phase, label, color, mult = "neutral",   "⚪ 中立",     "#8b949e", 1.00
    elif adj >= -10:
        phase, label, color, mult = "mild_bear", "🟠 やや弱気", "#f0883e", 0.85
    else:
        phase, label, color, mult = "bear",      "🔴 弱気",    "#f85149", 0.70

    result.update({
        "phase": phase, "phase_label": label, "phase_color": color,
        "score_multiplier": mult, "score_adj": adj,
        "warnings": warnings, "positives": positives
    })
    return result

# ─── 決算・配当情報の取得 ────────────────────────────────────
@st.cache_data(ttl=3600)
def get_earnings_info(ticker_code):
    """
    決算予定日・配当落ち日を取得して警告レベルを返す。
    戻り値: {
        earnings_date, days_to_earnings, earnings_warning,  # None / "danger" / "caution"
        ex_div_date,   days_to_ex_div,   div_warning
    }
    """
    info = {
        "earnings_date": None, "days_to_earnings": None, "earnings_warning": None,
        "ex_div_date": None,   "days_to_ex_div": None,   "div_warning": None
    }
    try:
        ticker = yf.Ticker(f"{ticker_code}.T")
        today  = datetime.now().date()

        # 決算日
        cal = ticker.calendar
        if cal is not None:
            if isinstance(cal, dict):
                eq = cal.get("Earnings Date")
                if eq:
                    # リスト or Timestamp
                    ed = eq[0] if isinstance(eq, list) else eq
                    if hasattr(ed, 'date'):
                        ed = ed.date()
                    elif isinstance(ed, str):
                        ed = datetime.strptime(ed[:10], "%Y-%m-%d").date()
                    days = (ed - today).days
                    if 0 <= days <= 30:
                        info["earnings_date"]    = ed
                        info["days_to_earnings"] = days
                        info["earnings_warning"] = "danger"  if days <= 7  else "caution"
            elif hasattr(cal, 'T'):
                # DataFrame形式
                try:
                    ed_row = cal.T.get("Earnings Date")
                    if ed_row is not None:
                        ed = pd.to_datetime(ed_row.values[0]).date()
                        days = (ed - today).days
                        if 0 <= days <= 30:
                            info["earnings_date"]    = ed
                            info["days_to_earnings"] = days
                            info["earnings_warning"] = "danger" if days <= 7 else "caution"
                except:
                    pass

        # 配当落ち日
        try:
            t_info = ticker.info
            ex_div = t_info.get("exDividendDate")
            if ex_div:
                if isinstance(ex_div, (int, float)):
                    ex_date = datetime.fromtimestamp(ex_div).date()
                else:
                    ex_date = pd.to_datetime(ex_div).date()
                days = (ex_date - today).days
                if 0 <= days <= 14:
                    info["ex_div_date"]   = ex_date
                    info["days_to_ex_div"] = days
                    info["div_warning"]   = "caution"
        except:
            pass

    except:
        pass
    return info

def analyze_stock(ticker_code, name, market_env=None, earnings_info=None):
    df = fetch_stock_data(ticker_code)
    if df is None or len(df) < 26:
        return None

    close = df['Close']
    volume = df['Volume']
    current_price = close.iloc[-1]

    # ─── 移動平均 ───
    ma5 = close.rolling(5).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(min(60, len(close))).mean().iloc[-1]

    # ─── RSI ───
    rsi = calc_rsi(close)
    rsi_now = rsi.iloc[-1]
    rsi_prev = rsi.iloc[-2]

    # ─── MACD ───
    macd, macd_signal, macd_hist = calc_macd(close)
    macd_now = macd.iloc[-1]
    macd_sig_now = macd_signal.iloc[-1]
    macd_hist_now = macd_hist.iloc[-1]
    macd_hist_prev = macd_hist.iloc[-2]

    # ─── ボリンジャーバンド ───
    bb_upper, bb_mid, bb_lower = calc_bollinger(close)
    bb_upper_now = bb_upper.iloc[-1]
    bb_lower_now = bb_lower.iloc[-1]
    bb_pct = (current_price - bb_lower_now) / (bb_upper_now - bb_lower_now) if (bb_upper_now - bb_lower_now) > 0 else 0.5

    # ─── 出来高 ───
    vol_avg = volume.rolling(20).mean().iloc[-1]
    vol_ratio = volume.iloc[-1] / vol_avg if vol_avg > 0 else 1.0

    # ─── 直近パフォーマンス ───
    pct_1d = (close.iloc[-1] / close.iloc[-2] - 1) * 100 if len(close) >= 2 else 0
    pct_5d = (close.iloc[-1] / close.iloc[-5] - 1) * 100 if len(close) >= 5 else 0
    pct_20d = (close.iloc[-1] / close.iloc[-20] - 1) * 100 if len(close) >= 20 else 0

    # ─── スコアリング（100点満点） ──────────────────────────
    score = 0
    signals = []
    reasons = []

    # RSIスコア（25点）
    rsi_score = 0
    if 30 <= rsi_now <= 50:  # 最も買いやすいゾーン
        rsi_score = 25
        signals.append("RSI買い圏")
        reasons.append(f"RSI={rsi_now:.1f}（30-50の買いゾーン）")
    elif 50 < rsi_now <= 60:
        rsi_score = 18
        signals.append("RSI中立上昇")
        reasons.append(f"RSI={rsi_now:.1f}（上昇トレンド継続）")
    elif 20 <= rsi_now < 30:
        rsi_score = 20
        signals.append("RSI売られすぎ")
        reasons.append(f"RSI={rsi_now:.1f}（売られすぎ・反発期待）")
    elif rsi_now > 70:
        rsi_score = 5
        reasons.append(f"RSI={rsi_now:.1f}（買われすぎ注意）")
    else:
        rsi_score = 10
        reasons.append(f"RSI={rsi_now:.1f}")

    # RSI上昇中ボーナス
    if rsi_now > rsi_prev and rsi_now < 70:
        rsi_score = min(25, rsi_score + 3)

    score += rsi_score

    # MACDスコア（25点）
    macd_score = 0
    if macd_now > macd_sig_now and macd_hist_now > macd_hist_prev:  # ゴールデンクロス後上昇中
        macd_score = 25
        signals.append("MACDゴールデン")
        reasons.append("MACDがシグナル上で拡大中（強い買いシグナル）")
    elif macd_now > macd_sig_now and macd_hist_now > 0:
        macd_score = 18
        signals.append("MACD陽転")
        reasons.append("MACDがシグナルを上回る（買いシグナル）")
    elif macd_hist_now > macd_hist_prev and macd_hist_now < 0:
        macd_score = 12
        signals.append("MACD底打ち")
        reasons.append("MACDヒストグラムが底打ち（反発兆候）")
    elif macd_now < macd_sig_now and macd_hist_now < macd_hist_prev:
        macd_score = 3
        reasons.append("MACDデッドクロス（売り圧力）")
    else:
        macd_score = 10
        reasons.append("MACD中立")

    score += macd_score

    # 移動平均スコア（20点）
    ma_score = 0
    if current_price > ma5 > ma20 > ma60:  # パーフェクトオーダー
        ma_score = 20
        signals.append("MA完全陽転")
        reasons.append("MA5>MA20>MA60のパーフェクトオーダー（強いトレンド）")
    elif current_price > ma20 and ma5 > ma20:
        ma_score = 14
        signals.append("MA上昇配列")
        reasons.append("MA5・MA20上向きでトレンド良好")
    elif current_price > ma20:
        ma_score = 10
        reasons.append("MA20上で推移（上昇バイアス）")
    elif current_price < ma20 and current_price > ma60:
        ma_score = 6
        reasons.append("MA20下でMA60上（調整局面）")
    else:
        ma_score = 2
        reasons.append("移動平均線下（下降トレンド）")

    score += ma_score

    # ボリンジャーバンドスコア（15点）
    bb_score = 0
    if bb_pct < 0.2:  # 下限付近
        bb_score = 15
        signals.append("BB下限反発")
        reasons.append(f"ボリンジャー下限付近（{bb_pct:.0%}）・反発期待大")
    elif 0.2 <= bb_pct < 0.4:
        bb_score = 12
        reasons.append(f"ボリンジャー下位（{bb_pct:.0%}）・買いやすい位置")
    elif 0.4 <= bb_pct < 0.6:
        bb_score = 8
        reasons.append(f"ボリンジャー中央付近（{bb_pct:.0%}）")
    elif bb_pct >= 0.8:  # 上限付近（買い辛い）
        bb_score = 2
        reasons.append(f"ボリンジャー上限近く（{bb_pct:.0%}）・高値注意")
    else:
        bb_score = 5
        reasons.append(f"ボリンジャー位置: {bb_pct:.0%}")

    score += bb_score

    # 出来高スコア（15点）
    vol_score = 0
    if vol_ratio >= 2.0:
        vol_score = 15
        signals.append("出来高急増")
        reasons.append(f"出来高が平均の{vol_ratio:.1f}倍（強い買い圧力）")
    elif vol_ratio >= 1.5:
        vol_score = 12
        signals.append("出来高増加")
        reasons.append(f"出来高が平均の{vol_ratio:.1f}倍（注目集まる）")
    elif vol_ratio >= 1.0:
        vol_score = 8
        reasons.append(f"出来高平均並み（{vol_ratio:.1f}倍）")
    else:
        vol_score = 3
        reasons.append(f"出来高少ない（{vol_ratio:.1f}倍）・流動性注意")

    score += vol_score

    # ─── 市場環境スコア加減点（±20点） ──────────────────────
    market_score_adj = 0
    market_reasons   = []
    if market_env:
        raw_adj = market_env.get("score_adj", 0)
        # 個別銘柄への影響は市場調整値の60%を加減点（最大±20点に正規化）
        market_score_adj = max(-20, min(10, int(raw_adj * 0.6)))
        phase_label = market_env.get("phase_label", "")
        if market_score_adj > 0:
            market_reasons.append(f"地合い良好（{phase_label}）+{market_score_adj}pt")
        elif market_score_adj < 0:
            market_reasons.append(f"地合い悪化（{phase_label}）{market_score_adj}pt")
        else:
            market_reasons.append(f"地合い中立（{phase_label}）")
    score += market_score_adj

    # ─── 決算・配当ペナルティ ────────────────────────────────
    earnings_score_adj = 0
    earnings_warning   = None
    div_warning        = None
    days_to_earnings   = None
    days_to_ex_div     = None
    if earnings_info:
        days_to_earnings = earnings_info.get("days_to_earnings")
        days_to_ex_div   = earnings_info.get("days_to_ex_div")
        if earnings_info.get("earnings_warning") == "danger":
            earnings_score_adj -= 20
            earnings_warning = "danger"
            reasons.append(f"⚠️ 決算{days_to_earnings}日前（エントリー要注意）")
        elif earnings_info.get("earnings_warning") == "caution":
            earnings_score_adj -= 10
            earnings_warning = "caution"
            reasons.append(f"📅 決算{days_to_earnings}日前（決算跨ぎリスクあり）")
        if earnings_info.get("div_warning") == "caution":
            earnings_score_adj -= 5
            div_warning = "caution"
            reasons.append(f"💴 配当落ち{days_to_ex_div}日前（需給変動に注意）")
    score += earnings_score_adj

    # スコアを0〜100にクランプ
    score = max(0.0, min(100.0, score))


    atr = calc_atr(df)

    # 直近スウィングハイ・ローを検出（20日）
    recent = df.tail(20)
    swing_lows, swing_highs = [], []
    lows = recent['Low'].values
    highs = recent['High'].values
    for idx in range(1, len(lows) - 1):
        if lows[idx] < lows[idx-1] and lows[idx] < lows[idx+1]:
            swing_lows.append(lows[idx])
        if highs[idx] > highs[idx-1] and highs[idx] > highs[idx+1]:
            swing_highs.append(highs[idx])

    # 現在値より下の最も近いサポート、上の最も近いレジスタンスを選ぶ
    nearest_support = max(
        [v for v in swing_lows if v < current_price],
        default=current_price - atr * 1.5
    )
    nearest_resistance = min(
        [v for v in swing_highs if v > current_price],
        default=current_price + atr * 3.0
    )
    recent_5d_low = df['Low'].tail(5).min()

    # ─── エントリー戦略の自動選択 ────────────────────────────
    # 戦略A: 押し目買い（トレンドフォロー）
    #   条件: MAパーフェクトオーダー or MA5>MA20、かつ現値がMA5またはMA20の±1ATR圧内
    dist_to_ma5  = abs(current_price - ma5)
    dist_to_ma20 = abs(current_price - ma20)
    near_ma5  = dist_to_ma5  < atr * 0.5
    near_ma20 = dist_to_ma20 < atr * 0.8
    trend_up = (ma5 > ma20) and (current_price > ma20)

    # 戦略B: BB下限反発（逆張り）
    #   条件: BB位置が20%以下、RSIが50以下で上向き
    strategy_b = (bb_pct < 0.25) and (rsi_now < 55) and (rsi_now > rsi_prev)

    # 戦略C: サポートライン反発
    #   条件: 現値がスウィングローの±ATR*0.3圏内
    near_support = abs(current_price - nearest_support) < atr * 0.4

    # 戦略D: ブレイクアウト
    #   条件: 出来高急増(1.8倍以上) + MACDヒストグラム拡大 + 現値がMA20を明確に上抜け
    breakout = (
        vol_ratio >= 1.8 and
        macd_hist_now > macd_hist_prev and
        macd_hist_now > 0 and
        current_price > ma20 * 1.005
    )

    # 戦略の優先順位: D > A(MA5) > A(MA20) > B > C > デフォルト
    if breakout:
        strategy_type = "D"
        strategy_label = "ブレイクアウト買い"
        strategy_desc  = f"出来高{vol_ratio:.1f}倍・MACD拡大・MA20上抜け → 勢い乗り"
        # ブレイク直後は現値より少し上で確認買い
        entry_price  = round(current_price * 1.002, 0)
        # 損切: MA20を割り込んだら即撤退
        stop_loss    = round(max(ma20 * 0.997, entry_price - atr * 1.0), 0)
        # 利確: 直近レジスタンスかATR×3.0
        take_profit  = round(min(nearest_resistance * 0.998,
                                  entry_price + atr * 3.0), 0)

    elif trend_up and near_ma5:
        strategy_type = "A1"
        strategy_label = "押し目買い（MA5タッチ）"
        strategy_desc  = f"上昇トレンド中のMA5({ma5:,.0f})押し目 → 反発狙い"
        # MA5より少し上で指値（タッチからの反発確認）
        entry_price  = round(ma5 * 1.001, 0)
        stop_loss    = round(ma5 - atr * 0.8, 0)
        take_profit  = round(min(nearest_resistance * 0.998,
                                  entry_price + atr * 2.5), 0)

    elif trend_up and near_ma20:
        strategy_type = "A2"
        strategy_label = "押し目買い（MA20タッチ）"
        strategy_desc  = f"上昇トレンド中のMA20({ma20:,.0f})押し目 → 中期線反発"
        entry_price  = round(ma20 * 1.001, 0)
        stop_loss    = round(ma20 - atr * 1.0, 0)
        take_profit  = round(min(nearest_resistance * 0.998,
                                  entry_price + atr * 3.0), 0)

    elif strategy_b:
        strategy_type = "B"
        strategy_label = "BB下限反発（逆張り）"
        strategy_desc  = f"BBバンド下限({bb_lower_now:,.0f})付近・RSI{rsi_now:.0f}で反発兆候"
        # BB下限より少し上で指値
        entry_price  = round(bb_lower_now * 1.002, 0)
        stop_loss    = round(bb_lower_now - atr * 0.5, 0)
        # 利確: BB中央線（MA20）を第1目標、BB上限を第2目標
        take_profit  = round(bb_mid.iloc[-1], 0)

    elif near_support:
        strategy_type = "C"
        strategy_label = "サポートライン反発"
        strategy_desc  = f"直近サポート({nearest_support:,.0f})タッチ → 水平線反発"
        entry_price  = round(nearest_support * 1.003, 0)
        stop_loss    = round(nearest_support * 0.990, 0)
        take_profit  = round(min(nearest_resistance * 0.998,
                                  entry_price + atr * 2.5), 0)

    else:
        # デフォルト: ATRベース（明確な戦略シグナルなし）
        strategy_type = "ATR"
        strategy_label = "ATRベース（標準）"
        strategy_desc  = "特定パターン未検出。ATR基準の標準エントリー"
        entry_price  = round(current_price * 0.997, 0)
        stop_loss    = round(entry_price - atr * 1.0, 0)
        take_profit  = round(entry_price + atr * 2.5, 0)

    # エントリー価格が現在値より大幅に乖離していたら補正
    if entry_price > current_price * 1.03:
        entry_price = round(current_price * 1.002, 0)
    if entry_price < current_price * 0.97:
        entry_price = round(current_price * 0.997, 0)

    # 損切りが現在値より上になるバグ防止
    if stop_loss >= entry_price:
        stop_loss = round(entry_price - atr * 1.0, 0)
    # 利確が現在値より下になるバグ防止
    if take_profit <= entry_price:
        take_profit = round(entry_price + atr * 2.5, 0)

    profit_pct = (take_profit / entry_price - 1) * 100
    loss_pct   = (stop_loss  / entry_price - 1) * 100
    rr_ratio   = profit_pct / abs(loss_pct) if loss_pct != 0 else 0

    return {
        "code": ticker_code,
        "name": name,
        "current_price": current_price,
        "entry_price": entry_price,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
        "profit_pct": profit_pct,
        "loss_pct": loss_pct,
        "rr_ratio": rr_ratio,
        "score": round(score, 1),
        "signals": signals,
        "reasons": reasons,
        "market_reasons": market_reasons,
        "market_score_adj": market_score_adj,
        "earnings_warning": earnings_warning,
        "div_warning": div_warning,
        "days_to_earnings": days_to_earnings,
        "days_to_ex_div": days_to_ex_div,
        "strategy_type": strategy_type,
        "strategy_label": strategy_label,
        "strategy_desc": strategy_desc,
        "rsi": rsi_now,
        "rsi_prev": rsi_prev,
        "macd_hist": macd_hist_now,
        "bb_pct": bb_pct,
        "bb_lower": bb_lower_now,
        "vol_ratio": vol_ratio,
        "pct_1d": pct_1d,
        "pct_5d": pct_5d,
        "pct_20d": pct_20d,
        "ma5": ma5,
        "ma20": ma20,
        "ma60": ma60,
        "nearest_support": nearest_support,
        "nearest_resistance": nearest_resistance,
        "df": df
    }

def calc_atr(df, period=14):
    high = df['High']
    low = df['Low']
    close = df['Close']
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean().iloc[-1]

# ─── ランキング計算 ───────────────────────────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def compute_rankings(_progress_callback=None):
    results  = []
    tickers  = list(NIKKEI225_TICKERS.items())

    # 市場環境を先に1回だけ取得
    progress_bar = st.progress(0, text="市場環境を分析中...")
    market_env   = calc_market_environment()

    for i, (code, name) in enumerate(tickers):
        progress_bar.progress(
            (i + 1) / len(tickers),
            text=f"分析中: {name} ({code})"
        )
        # 決算・配当情報取得
        earnings_info = get_earnings_info(code)
        result = analyze_stock(code, name,
                               market_env=market_env,
                               earnings_info=earnings_info)
        if result:
            results.append(result)

    progress_bar.empty()
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:20], market_env

def show_market_environment(env):
    """ランキングページ上部に市場環境バナーを表示"""
    if not env:
        return
    phase_color = env.get("phase_color", "#8b949e")
    phase_label = env.get("phase_label", "不明")
    nk_price    = env.get("nk_price")
    nk_1d       = env.get("nk_1d", 0.0)
    nk_5d       = env.get("nk_5d", 0.0)
    nk_rsi      = env.get("nk_rsi", 0.0)
    vix         = env.get("vix")
    vix_level   = env.get("vix_level", "normal")
    topix_5d    = env.get("topix_5d", 0.0)
    warnings    = env.get("warnings", [])
    positives   = env.get("positives", [])
    score_adj   = env.get("score_adj", 0)

    nk_1d_color  = "#3fb950" if nk_1d  >= 0 else "#f85149"
    nk_5d_color  = "#3fb950" if nk_5d  >= 0 else "#f85149"
    tp_5d_color  = "#3fb950" if topix_5d >= 0 else "#f85149"
    vix_color    = "#f85149" if vix_level == "high" else ("#f0883e" if vix_level == "elevated" else "#3fb950")
    adj_color    = "#3fb950" if score_adj >= 0 else "#f85149"
    adj_sign     = "+" if score_adj >= 0 else ""

    nk_str  = f"¥{nk_price:,.0f}" if nk_price else "---"
    vix_str = f"{vix:.1f}"        if vix      else "---"

    warn_html = "".join([
        f'<div style="color:#f85149; font-size:0.78rem; margin:2px 0;">⚠️ {w}</div>'
        for w in warnings
    ])
    pos_html = "".join([
        f'<div style="color:#3fb950; font-size:0.78rem; margin:2px 0;">✅ {p}</div>'
        for p in positives
    ])

    st.markdown(f"""
    <div style="background:#161b22; border:1px solid {phase_color};
                border-radius:12px; padding:18px 24px; margin-bottom:18px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
            <div>
                <span style="font-size:1.1rem; font-weight:700; color:{phase_color};">{phase_label}</span>
                <span style="color:#8b949e; font-size:0.8rem; margin-left:10px;">現在の市場環境</span>
            </div>
            <div style="text-align:right;">
                <span style="color:#8b949e; font-size:0.75rem;">全銘柄スコア補正：</span>
                <span style="color:{adj_color}; font-weight:700; font-family:'JetBrains Mono',monospace;">
                    {adj_sign}{score_adj}pt
                </span>
            </div>
        </div>
        <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:12px;
                    font-family:'JetBrains Mono',monospace; font-size:0.82rem; margin-bottom:14px;">
            <div>
                <div style="color:#8b949e; font-size:0.7rem; letter-spacing:1px;">日経225</div>
                <div style="color:#f0f6fc; font-weight:700;">{nk_str}</div>
            </div>
            <div>
                <div style="color:#8b949e; font-size:0.7rem; letter-spacing:1px;">日経 前日比</div>
                <div style="color:{nk_1d_color}; font-weight:700;">
                    {"+" if nk_1d >= 0 else ""}{nk_1d:.2f}%
                </div>
            </div>
            <div>
                <div style="color:#8b949e; font-size:0.7rem; letter-spacing:1px;">日経 5日</div>
                <div style="color:{nk_5d_color}; font-weight:700;">
                    {"+" if nk_5d >= 0 else ""}{nk_5d:.2f}%
                </div>
            </div>
            <div>
                <div style="color:#8b949e; font-size:0.7rem; letter-spacing:1px;">日経 RSI</div>
                <div style="color:#d2a8ff; font-weight:700;">{nk_rsi:.1f}</div>
            </div>
            <div>
                <div style="color:#8b949e; font-size:0.7rem; letter-spacing:1px;">VIX</div>
                <div style="color:{vix_color}; font-weight:700;">{vix_str}</div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div style="background:#0d1117; border-radius:8px; padding:10px;">
                <div style="color:#8b949e; font-size:0.7rem; margin-bottom:6px; letter-spacing:1px;">⚠️ 懸念事項</div>
                {warn_html if warn_html else '<div style="color:#8b949e;font-size:0.78rem;">特になし</div>'}
            </div>
            <div style="background:#0d1117; border-radius:8px; padding:10px;">
                <div style="color:#8b949e; font-size:0.7rem; margin-bottom:6px; letter-spacing:1px;">✅ ポジティブ要因</div>
                {pos_html if pos_html else '<div style="color:#8b949e;font-size:0.78rem;">特になし</div>'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── チャート描画 ─────────────────────────────────────────────
def draw_chart(stock_data):
    df = stock_data['df']
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("ローソク足 + ボリンジャーバンド + 移動平均", "MACD", "RSI"),
        vertical_spacing=0.05
    )

    # ローソク足（日本式：陽線=赤、陰線=青）
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="ローソク",
        increasing_line_color='#f85149',
        increasing_fillcolor='#f85149',
        decreasing_line_color='#4d9de0',
        decreasing_fillcolor='#4d9de0'
    ), row=1, col=1)

    # ボリンジャーバンド
    close = df['Close']
    bb_upper, bb_mid, bb_lower = calc_bollinger(close)
    fig.add_trace(go.Scatter(x=df.index, y=bb_upper, line=dict(color='rgba(120,120,255,0.5)', dash='dash'), name="BB上限"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=bb_lower, line=dict(color='rgba(120,120,255,0.5)', dash='dash'), fill='tonexty', fillcolor='rgba(120,120,255,0.05)', name="BB下限"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=bb_mid, line=dict(color='rgba(150,150,255,0.3)', dash='dot'), name="BB中央"), row=1, col=1)

    # 移動平均
    fig.add_trace(go.Scatter(x=df.index, y=close.rolling(5).mean(), line=dict(color='#ffa657', width=1), name="MA5"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=close.rolling(20).mean(), line=dict(color='#79c0ff', width=1.5), name="MA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=close.rolling(60).mean(), line=dict(color='#d2a8ff', width=1), name="MA60"), row=1, col=1)

    # エントリー・利確・損切りライン
    fig.add_hline(y=stock_data['entry_price'], line_color='#79c0ff', line_dash='dash', annotation_text="エントリー", row=1, col=1)
    fig.add_hline(y=stock_data['take_profit'], line_color='#3fb950', line_dash='dot', annotation_text="利確", row=1, col=1)
    fig.add_hline(y=stock_data['stop_loss'], line_color='#f85149', line_dash='dot', annotation_text="損切", row=1, col=1)

    # MACD
    macd, macd_signal, macd_hist = calc_macd(close)
    colors = ['#3fb950' if v >= 0 else '#f85149' for v in macd_hist]
    fig.add_trace(go.Bar(x=df.index, y=macd_hist, marker_color=colors, name="MACDヒスト", opacity=0.7), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=macd, line=dict(color='#79c0ff', width=1.5), name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=macd_signal, line=dict(color='#ffa657', width=1), name="シグナル"), row=2, col=1)

    # RSI
    rsi = calc_rsi(close)
    fig.add_trace(go.Scatter(x=df.index, y=rsi, line=dict(color='#d2a8ff', width=1.5), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, line_color='rgba(248,81,73,0.4)', line_dash='dash', row=3, col=1)
    fig.add_hline(y=30, line_color='rgba(63,185,80,0.4)', line_dash='dash', row=3, col=1)

    fig.update_layout(
        paper_bgcolor='#0d1117', plot_bgcolor='#161b22',
        font_color='#c9d1d9', height=650,
        xaxis_rangeslider_visible=False,
        margin=dict(t=40, b=20, l=60, r=40),
        legend=dict(orientation='h', y=1.02, bgcolor='rgba(0,0,0,0)'),
        showlegend=True
    )
    for axis in ['xaxis', 'yaxis', 'xaxis2', 'yaxis2', 'xaxis3', 'yaxis3']:
        fig.update_layout(**{axis: dict(gridcolor='#21262d', linecolor='#30363d')})

    return fig

# ─── IFDOCO注文の表示 ─────────────────────────────────────────
def show_ifdoco_order(stock):
    st.markdown(f"""
    <div class="order-box">
        <div style="margin-bottom:12px; color:#8b949e; font-size:0.7rem; letter-spacing:1px;">■ IFDOCO注文（信用取引）</div>
        <table style="width:100%; border-collapse:collapse;">
            <tr>
                <td style="padding:4px 0; width:40%; color:#8b949e; font-size:0.75rem;">IF（新規エントリー）</td>
                <td style="padding:4px 0; color:#79c0ff; font-weight:700; font-size:0.95rem;">
                    買い ¥{stock['entry_price']:,.0f} 指値
                </td>
            </tr>
            <tr><td colspan="2" style="border-top:1px solid #21262d; padding:6px 0;"></td></tr>
            <tr>
                <td style="padding:4px 0; color:#8b949e; font-size:0.75rem;">OCO①（利確）</td>
                <td style="padding:4px 0; color:#3fb950; font-weight:700; font-size:0.95rem;">
                    売り ¥{stock['take_profit']:,.0f} 指値
                    <span style="color:#8b949e; font-size:0.75rem;">(+{stock['profit_pct']:.1f}%)</span>
                </td>
            </tr>
            <tr>
                <td style="padding:4px 0; color:#8b949e; font-size:0.75rem;">OCO②（損切）</td>
                <td style="padding:4px 0; color:#f85149; font-weight:700; font-size:0.95rem;">
                    売り ¥{stock['stop_loss']:,.0f} 逆指値
                    <span style="color:#8b949e; font-size:0.75rem;">({stock['loss_pct']:.1f}%)</span>
                </td>
            </tr>
            <tr><td colspan="2" style="border-top:1px solid #21262d; padding:6px 0;"></td></tr>
            <tr>
                <td style="padding:4px 0; color:#8b949e; font-size:0.75rem;">リスクリワード比</td>
                <td style="padding:4px 0; color:#ffa657; font-weight:700;">1 : {stock['rr_ratio']:.2f}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ─── 信用取引の口数計算 ──────────────────────────────────────
def calc_margin_units(capital, price, margin_rate=0.3):
    """保証金率30%での信用取引可能株数を計算"""
    buying_power = capital / margin_rate  # 信用枠
    units = int((buying_power * 0.3) / price / 100) * 100  # 1銘柄に資金の30%まで
    return max(units, 100)

def fetch_stock_name(ticker_code):
    """銘柄コードから銘柄名を取得（日経225リストを優先し、なければyfinanceから取得）"""
    if ticker_code in NIKKEI225_TICKERS:
        return NIKKEI225_TICKERS[ticker_code]
    try:
        ticker = yf.Ticker(f"{ticker_code}.T")
        info = ticker.info
        name = info.get("longName") or info.get("shortName") or ticker_code
        return name
    except:
        return ticker_code

def calc_recommended_tp_sl(ticker_code, entry_price):
    """ATRベースで推奨利確・損切り価格を計算"""
    try:
        df = fetch_stock_data(ticker_code)
        if df is None:
            return round(entry_price * 1.05, 0), round(entry_price * 0.97, 0)
        atr = calc_atr(df)
        take_profit = round(entry_price + atr * 2.5, 0)
        stop_loss = round(entry_price - atr * 1.0, 0)
        return take_profit, stop_loss
    except:
        return round(entry_price * 1.05, 0), round(entry_price * 0.97, 0)

# ─── ポートフォリオ管理 ──────────────────────────────────────
def portfolio_section(portfolio):
    st.markdown('<div class="section-header">📂 保有株管理</div>', unsafe_allow_html=True)

    cap = portfolio.get("account_capital", 3000000)
    target = portfolio.get("monthly_target", 200000)

    # サマリー
    positions = portfolio.get("positions", [])
    total_pl = 0
    for pos in positions:
        current = get_current_price(pos['code'])
        if current:
            pl = (current - pos['entry_price']) * pos['units']
            total_pl += pl

    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">¥{cap:,.0f}</div>
            <div class="metric-label">運用資金</div>
        </div>""", unsafe_allow_html=True)
    with cols[1]:
        pl_color = "#3fb950" if total_pl >= 0 else "#f85149"
        sign = "+" if total_pl >= 0 else ""
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{pl_color};">{sign}¥{total_pl:,.0f}</div>
            <div class="metric-label">含み損益</div>
        </div>""", unsafe_allow_html=True)
    with cols[2]:
        monthly_pct = (target / cap * 100)
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#ffa657;">¥{target:,.0f}</div>
            <div class="metric-label">月間目標（{monthly_pct:.1f}%）</div>
        </div>""", unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{len(positions)}</div>
            <div class="metric-label">保有銘柄数</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # 設定変更
    with st.expander("⚙️ アカウント設定"):
        c1, c2 = st.columns(2)
        with c1:
            new_cap = st.number_input("運用資金（円）", value=float(cap), step=100000.0, min_value=0.0)
        with c2:
            new_target = st.number_input("月間目標利益（円）", value=float(target), step=10000.0, min_value=0.0)
        if st.button("設定を保存"):
            portfolio["account_capital"] = new_cap
            portfolio["monthly_target"] = new_target
            save_portfolio(portfolio)
            st.success("✅ 設定を保存しました")
            st.rerun()

    # 新規ポジション追加
    with st.expander("➕ 新規ポジション追加"):
        st.markdown('<div style="color:#8b949e; font-size:0.8rem; margin-bottom:12px;">銘柄コードと取得単価・株数を入力すると、銘柄名の自動取得と利確・損切りの推奨値を計算します。</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            new_code = st.text_input("銘柄コード", placeholder="例：7203", key="new_pos_code")
        with c2:
            new_entry = st.number_input("取得単価（円）", min_value=0.0, step=10.0, key="new_pos_entry")
        with c3:
            new_units = st.number_input("株数", min_value=0, step=100, value=100, key="new_pos_units")

        # 銘柄コードと取得単価が入力されたら自動計算して表示
        if new_code and len(new_code) >= 4 and new_entry > 0:
            auto_name = fetch_stock_name(new_code.strip())
            rec_tp, rec_sl = calc_recommended_tp_sl(new_code.strip(), new_entry)
            profit_pct = (rec_tp / new_entry - 1) * 100
            loss_pct = (rec_sl / new_entry - 1) * 100
            rr = profit_pct / abs(loss_pct) if loss_pct != 0 else 0
            est_pl_profit = (rec_tp - new_entry) * new_units
            est_pl_loss = (new_entry - rec_sl) * new_units

            st.markdown(f"""
            <div style="background:#0d1117; border:1px solid #30363d; border-radius:10px; padding:16px; margin-top:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div>
                        <span style="color:#f0f6fc; font-weight:700; font-size:1.05rem;">{auto_name}</span>
                        <span style="color:#8b949e; font-size:0.8rem; margin-left:8px;">{new_code.strip()}</span>
                    </div>
                    <span style="color:#8b949e; font-size:0.75rem;">銘柄名・推奨値を自動計算</span>
                </div>
                <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; font-family:'JetBrains Mono',monospace; font-size:0.82rem;">
                    <div>
                        <div class="order-label">推奨 利確目標</div>
                        <div style="color:#3fb950; font-weight:700; font-size:1rem;">¥{rec_tp:,.0f}</div>
                        <div style="color:#8b949e; font-size:0.72rem;">+{profit_pct:.1f}%　期待利益: +¥{est_pl_profit:,.0f}</div>
                    </div>
                    <div>
                        <div class="order-label">推奨 損切ライン</div>
                        <div style="color:#f85149; font-weight:700; font-size:1rem;">¥{rec_sl:,.0f}</div>
                        <div style="color:#8b949e; font-size:0.72rem;">{loss_pct:.1f}%　リスク: -¥{est_pl_loss:,.0f}</div>
                    </div>
                    <div>
                        <div class="order-label">リスクリワード比</div>
                        <div style="color:#ffa657; font-weight:700; font-size:1rem;">1 : {rr:.2f}</div>
                        <div style="color:#8b949e; font-size:0.72rem;">ATRベース自動計算</div>
                    </div>
                    <div>
                        <div class="order-label">取得コスト（現物）</div>
                        <div style="color:#79c0ff; font-weight:700; font-size:1rem;">¥{new_entry * new_units:,.0f}</div>
                        <div style="color:#8b949e; font-size:0.72rem;">{new_units:,}株 @ ¥{new_entry:,.0f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")
            if st.button(f"📌 {auto_name}（{new_code.strip()}）をポートフォリオに追加", key="add_position_btn"):
                portfolio["positions"].append({
                    "code": new_code.strip(),
                    "name": auto_name,
                    "entry_price": float(new_entry),
                    "units": int(new_units),
                    "take_profit": float(rec_tp),
                    "stop_loss": float(rec_sl),
                })
                save_portfolio(portfolio)
                st.success(f"✅ {auto_name} をポートフォリオに追加しました！")
                st.rerun()
        else:
            st.markdown('<div style="color:#8b949e; font-size:0.8rem; padding:8px 0;">↑ 銘柄コードと取得単価を入力すると、推奨利確・損切りが自動で表示されます</div>', unsafe_allow_html=True)

    # 保有ポジション一覧
    if not positions:
        st.info("保有ポジションがありません。「新規ポジション追加」から追加してください。")
        return

    st.markdown("#### 現在の保有ポジション")

    for i, pos in enumerate(positions):
        current_price = get_current_price(pos['code'])
        if current_price:
            pl = (current_price - pos['entry_price']) * pos['units']
            pl_pct = (current_price / pos['entry_price'] - 1) * 100
            pl_color = "#3fb950" if pl >= 0 else "#f85149"
            sign = "+" if pl >= 0 else ""

            # 利確・損切りまでの距離
            tp_dist = ((pos.get('take_profit', 0) / current_price) - 1) * 100 if pos.get('take_profit', 0) > 0 else None
            sl_dist = ((pos.get('stop_loss', 0) / current_price) - 1) * 100 if pos.get('stop_loss', 0) > 0 else None

            status = "HOLD"
            if pos.get('take_profit', 0) > 0 and current_price >= pos['take_profit']:
                status = "利確推奨"
            elif pos.get('stop_loss', 0) > 0 and current_price <= pos['stop_loss']:
                status = "損切推奨"

            badge_class = "badge-profit" if "利確" in status else ("badge-loss" if "損切" in status else "badge-hold")

            with st.container():
                st.markdown(f"""
                <div class="portfolio-row">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div>
                            <span style="color:#f0f6fc; font-weight:700; font-size:1rem;">{pos['name']}</span>
                            <span style="color:#8b949e; font-size:0.8rem; margin-left:8px;">{pos['code']}</span>
                            <span style="font-size:0.75rem;" class="{badge_class}"> {status} </span>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:{pl_color}; font-weight:700; font-size:1.1rem;">{sign}¥{pl:,.0f}</span>
                            <span style="color:{pl_color}; font-size:0.8rem; margin-left:4px;">({sign}{pl_pct:.1f}%)</span>
                        </div>
                    </div>
                    <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:8px; font-size:0.78rem;">
                        <div><div class="order-label">現在値</div><div style="color:#79c0ff;font-weight:600;">¥{current_price:,.0f}</div></div>
                        <div><div class="order-label">取得単価</div><div style="color:#f0f6fc;">¥{pos['entry_price']:,.0f}</div></div>
                        <div><div class="order-label">株数</div><div style="color:#f0f6fc;">{pos['units']:,}株</div></div>
                        <div><div class="order-label">利確目標</div><div style="color:#3fb950;">¥{pos.get('take_profit', 0):,.0f} {'({:.1f}%)'.format(tp_dist) if tp_dist else ''}</div></div>
                        <div><div class="order-label">損切ライン</div><div style="color:#f85149;">¥{pos.get('stop_loss', 0):,.0f} {'({:.1f}%)'.format(sl_dist) if sl_dist else ''}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 利確/損切り調整 & クローズ
            with st.expander(f"⚙️ {pos['name']} の調整・クローズ"):
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    new_tp_val = st.number_input(f"利確目標を更新", value=float(pos.get('take_profit', current_price * 1.05)), step=10.0, key=f"tp_{i}")
                with cc2:
                    new_sl_val = st.number_input(f"損切ラインを更新", value=float(pos.get('stop_loss', current_price * 0.97)), step=10.0, key=f"sl_{i}")
                with cc3:
                    st.write("")
                    if st.button("更新", key=f"update_{i}"):
                        portfolio["positions"][i]["take_profit"] = new_tp_val
                        portfolio["positions"][i]["stop_loss"] = new_sl_val
                        save_portfolio(portfolio)
                        st.success("✅ 更新しました")
                        st.rerun()

                close_price_inp = st.number_input("クローズ価格（決済）", value=float(current_price), step=1.0, key=f"close_{i}")
                if st.button(f"🔴 {pos['name']} をクローズ（ポジション削除）", key=f"close_btn_{i}"):
                    realized_pl = (float(close_price_inp) - float(pos['entry_price'])) * int(pos['units'])
                    portfolio["account_capital"] = float(portfolio.get("account_capital", 3000000)) + realized_pl
                    portfolio["positions"].pop(i)
                    save_portfolio(portfolio)
                    st.success(f"✅ {pos['name']} をクローズ。実現損益: {'+' if realized_pl >= 0 else ''}¥{realized_pl:,.0f}")
                    st.rerun()

# ─── メインアプリ ─────────────────────────────────────────────
def main():
    portfolio = load_portfolio()

    # セッション状態初期化
    if "rankings_loaded" not in st.session_state:
        st.session_state.rankings_loaded = False
    if "rankings_data" not in st.session_state:
        st.session_state.rankings_data = []
    if "market_env_data" not in st.session_state:
        st.session_state.market_env_data = {}

    # ヘッダー
    st.markdown("""
    <div class="tool-header">
        <div>
            <div class="tool-title">📈 日経225 スイングトレード分析</div>
            <div class="tool-subtitle">信用取引 × IFDOCO注文 × テクニカルスコアリング</div>
        </div>
        <div style="text-align:right; color:#8b949e; font-size:0.8rem;">
            運用目標: <span style="color:#ffa657; font-weight:700;">月次 ¥200,000+</span><br>
            <span id="last-update">最終更新: {}</span>
        </div>
    </div>
    """.format(datetime.now().strftime("%Y/%m/%d %H:%M")), unsafe_allow_html=True)

    # サイドバー
    with st.sidebar:
        st.markdown("### 📊 ナビゲーション")
        page = st.radio("", ["🏆 銘柄ランキング", "📂 保有株管理"], label_visibility="collapsed")

        st.markdown("---")
        st.markdown("### ⚙️ スコアフィルター")
        min_score = st.slider("最低スコア", 0, 100, 50)
        min_rr = st.slider("最低リスクリワード比", 0.5, 5.0, 1.5, step=0.1)

        st.markdown("---")
        st.markdown("### 🕐 取引時間帯")
        st.markdown("""
        <div style="background:#161b22; border-radius:8px; padding:12px; font-size:0.8rem; color:#8b949e; border:1px solid #30363d;">
            ✅ <b style="color:#3fb950;">12:00〜13:00</b> 昼休み<br>
            ✅ <b style="color:#3fb950;">18:00〜</b> 夜間確認<br>
            📌 IFDOCO注文で自動執行
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🔄 ランキング更新", use_container_width=True):
            compute_rankings.clear()
            calc_market_environment.clear()
            st.session_state.rankings_loaded  = False
            st.session_state.rankings_data    = []
            st.session_state.market_env_data  = {}
            st.rerun()

    if "ランキング" in page:
        st.markdown('<div class="section-header">🏆 投資スコア ランキング TOP20（日経225）</div>', unsafe_allow_html=True)
        st.caption("💡 テクニカル指標（RSI・MACD・BB・MA・出来高）を総合スコアリング。スイングトレード（数日〜2週間）に最適化。")

        # 未ロード時はボタンを表示
        if not st.session_state.rankings_loaded:
            st.markdown("""
            <div style="background:#161b22; border:1px solid #30363d; border-radius:12px; padding:32px; text-align:center; margin:24px 0;">
                <div style="font-size:2.5rem; margin-bottom:12px;">📊</div>
                <div style="color:#f0f6fc; font-size:1.1rem; font-weight:700; margin-bottom:8px;">ランキングを取得する</div>
                <div style="color:#8b949e; font-size:0.85rem; margin-bottom:20px;">日経225全銘柄をテクニカル分析します（約30〜60秒）<br>サイドバーの「🔄 ランキング更新」ボタンを押すと最新データで再計算します</div>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📈 ランキングを取得する", use_container_width=True):
                    with st.spinner("銘柄データを取得・分析中...（しばらくお待ちください）"):
                        rankings, market_env = compute_rankings()
                    st.session_state.rankings_data   = rankings
                    st.session_state.market_env_data = market_env
                    st.session_state.rankings_loaded = True
                    st.rerun()
            return

        rankings   = st.session_state.rankings_data
        market_env = st.session_state.get("market_env_data", {})

        # 市場環境バナー
        show_market_environment(market_env)

        # フィルタリング
        filtered = [r for r in rankings if r['score'] >= min_score and r['rr_ratio'] >= min_rr]

        if not filtered:
            st.warning("現在の条件に合う銘柄がありません。フィルターを緩めてください。")
            return

        # ランキング表示
        selected_stock = None
        for i, stock in enumerate(filtered):
            rank = i + 1
            card_class = "gold" if rank == 1 else ("silver" if rank == 2 else ("bronze" if rank == 3 else "normal"))
            rank_icon = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))

            score_pct = stock['score']
            signals_html = "".join([
                f'<span class="signal-tag tag-buy">{s}</span>' for s in stock['signals'][:3]
            ])

            # 戦略タイプのバッジ色
            stype = stock.get('strategy_type', 'ATR')
            strat_colors = {
                "D":   ("#ff9500", "#3a2500", "🚀"),
                "A1":  ("#79c0ff", "#0d2a45", "📐"),
                "A2":  ("#79c0ff", "#0d2a45", "📐"),
                "B":   ("#d2a8ff", "#2a1a45", "↩️"),
                "C":   ("#3fb950", "#0d2a1a", "🏗️"),
                "ATR": ("#8b949e", "#21262d", "📊"),
            }
            sc, sbg, sicon = strat_colors.get(stype, strat_colors["ATR"])
            strategy_badge = f'<span style="background:{sbg};color:{sc};border:1px solid {sc};padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;font-family:\'JetBrains Mono\',monospace;">{sicon} {stock.get("strategy_label","")}</span>'

            # 決算・配当・地合いバッジ生成
            ew = stock.get("earnings_warning")
            dw = stock.get("div_warning")
            dte = stock.get("days_to_earnings")
            dtd = stock.get("days_to_ex_div")
            madj = stock.get("market_score_adj", 0)

            if ew == "danger":
                earnings_badge_html = f'<span style="background:#4a0d0d;color:#f85149;border:1px solid #f85149;padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;">🚨 決算{dte}日前・エントリー危険</span>'
            elif ew == "caution":
                earnings_badge_html = f'<span style="background:#3a2500;color:#ffa657;border:1px solid #f0883e;padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;">⚠️ 決算{dte}日前・要注意</span>'
            else:
                earnings_badge_html = ""

            if dw == "caution":
                div_badge_html = f'<span style="background:#1a2a3a;color:#79c0ff;border:1px solid #388bfd;padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;">💴 配当落ち{dtd}日前</span>'
            else:
                div_badge_html = ""

            if madj > 0:
                market_adj_html = f'<span style="background:#0d2a1a;color:#3fb950;border:1px solid #238636;padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;">📈 地合いボーナス +{madj}pt</span>'
            elif madj < 0:
                market_adj_html = f'<span style="background:#2a1a1a;color:#f85149;border:1px solid #f85149;padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;">📉 地合いペナルティ {madj}pt</span>'
            else:
                market_adj_html = ""


            pct5_color = "#3fb950" if stock['pct_5d'] >= 0 else "#f85149"
            sign1d = "+" if stock['pct_1d'] >= 0 else ""
            sign5d = "+" if stock['pct_5d'] >= 0 else ""

            st.markdown(f"""
            <div class="rank-card {card_class}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:1.4rem;">{rank_icon}</span>
                        <div>
                            <div style="color:#f0f6fc; font-weight:700; font-size:1rem;">{stock['name']}</div>
                            <div style="color:#8b949e; font-size:0.75rem;">東証プライム / {stock['code']}</div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:#ffa657; font-size:1.6rem; font-weight:700; font-family:'JetBrains Mono',monospace;">{stock['score']:.0f}<span style="font-size:0.8rem;color:#8b949e;">/100</span></div>
                        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{score_pct}%;"></div></div>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin:10px 0; font-family:'JetBrains Mono',monospace; font-size:0.82rem;">
                    <div><div class="order-label">現在値</div><div style="color:#f0f6fc; font-weight:600;">¥{stock['current_price']:,.0f}</div></div>
                    <div><div class="order-label">エントリー</div><div class="order-entry">¥{stock['entry_price']:,.0f}</div></div>
                    <div><div class="order-label">利確目標</div><div class="order-profit">¥{stock['take_profit']:,.0f} (+{stock['profit_pct']:.1f}%)</div></div>
                    <div><div class="order-label">損切ライン</div><div class="order-loss">¥{stock['stop_loss']:,.0f} ({stock['loss_pct']:.1f}%)</div></div>
                    <div><div class="order-label">RR比</div><div style="color:#ffa657; font-weight:600;">1:{stock['rr_ratio']:.1f}</div></div>
                </div>
                <div style="margin:8px 0;">{strategy_badge}&nbsp;&nbsp;{signals_html}</div>
                <div style="margin:4px 0; display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
                    {earnings_badge_html}
                    {div_badge_html}
                    {market_adj_html}
                </div>
                <div style="background:#0d1117; border-radius:6px; padding:10px; margin-top:8px; font-size:0.78rem; color:#8b949e;">
                    <strong style="color:#f0f6fc;">🎯 エントリー根拠：</strong><span style="color:{sc};">{stock.get('strategy_desc','')}</span>
                </div>
                <div style="background:#0d1117; border-radius:6px; padding:10px; margin-top:6px; font-size:0.78rem; color:#8b949e;">
                    <strong style="color:#f0f6fc;">📊 スコア解説：</strong>
                    {'　|　'.join(stock['reasons'][:4])}
                </div>
                <div style="margin-top:8px; font-size:0.75rem; display:flex; gap:16px;">
                    <span>1日: <b style="color:{pct_color};">{sign1d}{stock['pct_1d']:.1f}%</b></span>
                    <span>5日: <b style="color:{pct5_color};">{sign5d}{stock['pct_5d']:.1f}%</b></span>
                    <span>RSI: <b style="color:#d2a8ff;">{stock['rsi']:.1f}</b></span>
                    <span>BB位置: <b style="color:#79c0ff;">{stock['bb_pct']:.0%}</b></span>
                    <span>出来高比: <b style="color:#ffa657;">{stock['vol_ratio']:.1f}x</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # チャートとIFDOCO注文
            with st.expander(f"📈 {stock['name']} の詳細チャート・IFDOCO注文"):
                ch_col, order_col = st.columns([3, 1])
                with ch_col:
                    fig = draw_chart(stock)
                    st.plotly_chart(fig, use_container_width=True)
                with order_col:
                    # 信用取引の口数計算
                    capital = portfolio.get("account_capital", 3000000)
                    units = calc_margin_units(capital, stock['entry_price'])
                    cost = stock['entry_price'] * units
                    est_profit = (stock['take_profit'] - stock['entry_price']) * units
                    est_loss = (stock['entry_price'] - stock['stop_loss']) * units

                    st.markdown(f"""
                    <div style="margin-bottom:12px; background:#161b22; border:1px solid #30363d; border-radius:8px; padding:12px;">
                        <div class="order-label">推奨株数（信用3倍）</div>
                        <div style="color:#ffa657; font-size:1.3rem; font-weight:700; margin:4px 0;">{units:,} 株</div>
                        <div class="order-label">想定コスト（信用枠）</div>
                        <div style="color:#f0f6fc; font-size:0.85rem;">¥{cost:,.0f}</div>
                        <div style="margin-top:8px;">
                            <div class="order-label">期待利益</div>
                            <div style="color:#3fb950; font-weight:600;">+¥{est_profit:,.0f}</div>
                            <div class="order-label">リスク金額</div>
                            <div style="color:#f85149; font-weight:600;">-¥{est_loss:,.0f}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    show_ifdoco_order(stock)

                    # ポートフォリオに追加ボタン
                    if st.button(f"📌 {stock['code']} をポートフォリオに追加", key=f"add_{stock['code']}"):
                        portfolio["positions"].append({
                            "code": stock['code'],
                            "name": stock['name'],
                            "entry_price": stock['entry_price'],
                            "units": units,
                            "take_profit": stock['take_profit'],
                            "stop_loss": stock['stop_loss'],
                        })
                        save_portfolio(portfolio)
                        st.success(f"✅ {stock['name']} を追加しました！")

    # ─── ポートフォリオページ ────────────────────────────────
    else:
        portfolio_section(portfolio)

if __name__ == "__main__":
    main()
