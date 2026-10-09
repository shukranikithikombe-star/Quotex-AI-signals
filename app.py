import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="QUOTEX AI - Binary Signals", layout="wide", page_icon="🔥")

QUOTEX_MARKETS = {
    "EUR/USD OTC - Quotex": "EURUSD=X",
    "GBP/USD OTC - Quotex": "GBPUSD=X",
    "USD/JPY OTC - Quotex": "JPY=X",
    "GOLD OTC - Quotex": "GC=F",
    "BTC/USD OTC - Quotex": "BTC-USD",
    "Crypto IDX - Quotex": "BTC-USD"
}

st.title("🔥 QUOTEX BINARY AI - 1 MIN SIGNALS")

asset = st.selectbox("🎯 QUOTEX Asset", list(QUOTEX_MARKETS.keys()))
expiry = st.selectbox("⏱️ Expiry", ["30 Seconds", "1 Minute", "2 Minutes", "5 Minutes"], index=1)
ticker = QUOTEX_MARKETS[asset]
interval = "1m"

@st.cache_data(ttl=20)
def get_data(ticker, interval):
    df = yf.download(ticker, period="2d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

df = get_data(ticker, interval)
if len(df) < 30:
    st.error("Loading...")
    st.stop()

df['EMA5'] = ta.trend.ema_indicator(df['Close'], 5)
df['EMA13'] = ta.trend.ema_indicator(df['Close'], 13)
df['RSI'] = ta.momentum.rsi(df['Close'], 7)
df['MACD'] = ta.trend.macd_diff(df['Close'])
last = df.iloc[-1]
prev = df.iloc[-2]

buy, sell = 0, 0
reasons = []

if last['EMA5'] > last['EMA13'] and prev['EMA5'] <= prev['EMA13']:
    buy += 3; reasons.append("🟢 EMA 5 Crossed UP - CALL")
elif last['EMA5'] < last['EMA13'] and prev['EMA5'] >= prev['EMA13']:
    sell += 3; reasons.append("🔴 EMA 5 Crossed DOWN - PUT")
elif last['EMA5'] > last['EMA13']:
    buy += 1; reasons.append("↗️ EMA Uptrend")
else:
    sell += 1; reasons.append("↘️ EMA Downtrend")

if last['RSI'] < 25:
    buy += 3; reasons.append(f"🟢 RSI {last['RSI']:.0f} OVERSOLD - CALL")
elif last['RSI'] > 75:
    sell += 3; reasons.append(f"🔴 RSI {last['RSI']:.0f} OVERBOUGHT - PUT")

if last['Close'] > last['EMA13']:
    buy += 1
else:
    sell += 1

st.divider()
if buy >= 3 and buy > sell:
    st.markdown(f"<div style='background:#00c853;padding:25px;border-radius:15px;text-align:center'><h1 style='color:white'>💹 CALL ⬆️ {min(95,60+buy*10)}%</h1><h3 style='color:white'>BUY on {asset} for {expiry}</h3></div>", unsafe_allow_html=True)
elif sell >= 3 and sell > buy:
    st.markdown(f"<div style='background:#d50000;padding:25px;border-radius:15px;text-align:center'><h1 style='color:white'>📉 PUT ⬇️ {min(95,60+sell*10)}%</h1><h3 style='color:white'>SELL on {asset} for {expiry}</h3></div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='background:#333;padding:25px;border-radius:15px;text-align:center'><h1 style='color:#ffab00'>⏳ WAIT</h1><p style='color:white'>No clear setup - try another asset</p></div>", unsafe_allow_html=True)

for r in reasons:
    st.write(r)

fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index[-50:], open=df['Open'][-50:], high=df['High'][-50:], low=df['Low'][-50:], close=df['Close'][-50:]))
fig.add_trace(go.Scatter(x=df.index[-50:], y=df['EMA5'][-50:], name="EMA5"))
fig.add_trace(go.Scatter(x=df.index[-50:], y=df['EMA13'][-50:], name="EMA13"))
fig.update_layout(height=350, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
st.caption(f"Price: {last['Close']:.5f} | Time: {datetime.now().strftime('%H:%M:%S')} EAT | For Quotex Binary Only - High Risk")