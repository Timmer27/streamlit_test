import requests
import pandas as pd
import streamlit as st
import time

# Fetch Bithumb Data
def fetch_bithumb_tickers():
    url = 'https://api.bithumb.com/public/ticker/ALL_KRW'
    response = requests.get(url)
    data = response.json()
    tickers = {}
    for symbol, details in data['data'].items():
        if symbol != 'date':
            tickers[symbol] = float(details['closing_price'])
    return tickers

# Fetch Gopax Data
def fetch_gopax_tickers():
    url = 'https://api.gopax.co.kr/trading-pairs'
    response = requests.get(url)
    data = response.json()
    tickers = {}
    for pair in data:
        if pair['quoteAsset'] == 'KRW':
            symbol = pair['baseAsset']
            ticker_url = f"https://api.gopax.co.kr/trading-pairs/{symbol}-KRW/ticker"
            ticker_response = requests.get(ticker_url)
            ticker_data = ticker_response.json()
            tickers[symbol] = float(ticker_data['price'])
    return tickers

# Compare Prices
def compare_prices(price_diff_threshold: float):
    bithumb_tickers = fetch_bithumb_tickers()
    gopax_tickers = fetch_gopax_tickers()
    common_tickers = set(bithumb_tickers.keys()).intersection(gopax_tickers.keys())
    data = []

    for ticker in common_tickers:
        try:
            bithumb_price = bithumb_tickers[ticker]
            gopax_price = gopax_tickers[ticker]

            price_diff = abs(bithumb_price - gopax_price)
            price_diff_pct = price_diff / bithumb_price * 100 if bithumb_price > 0 else 0

            if price_diff_pct >= price_diff_threshold:
                data.append({
                    "Ticker": ticker,
                    "Bithumb 가격 (KRW)": bithumb_price,
                    "Gopax 가격 (KRW)": gopax_price,
                    "Price 가격차이 (KRW)": round(price_diff, 2),
                    "가격차이 (%)": round(price_diff_pct, 2)
                })
        except Exception as e:
            continue

    return pd.DataFrame(data)

# Streamlit App
st.title("Bithumb vs Gopax 가격 변동 탐지기")

# Slider for Price Difference Threshold
threshold = st.slider("가격 변동률 설정(%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)

# Refresh Data Every 10 Seconds
st.write("데이터 받아오는 중 (10초 주기)... 거래소 API 호출 속도로 인해 시간은 느릴 수 있습니다.")
with st.empty():
    while True:
        # Fetch and display data
        data = compare_prices(threshold)
        if not data.empty:
            st.dataframe(data)
        else:
            st.write("No significant price differences found.")

        # Wait for 10 seconds
        time.sleep(10)
