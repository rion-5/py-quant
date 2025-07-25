# strategies/momentum.py

import pandas as pd
from strategies.sortino_ratio import calculate_sortino_ratio
from data.data_fetcher import fetch_stock_data_from_db, fetch_stock_data_from_yfinance
from datetime import datetime, timedelta
import logging
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_stock_data(ticker, start_date, end_date):
    """DB 또는 yfinance에서 주식 데이터 조회"""
    start_date = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
    
    data = fetch_stock_data_from_db(ticker, start_date, end_date)
    if data.empty:
        logger.warning(f"No DB data for {ticker}, fetching from yfinance")
        data = fetch_stock_data_from_yfinance(ticker, start_date, end_date)
        if not data:
            return pd.DataFrame()
    
    data['Daily Return'] = data['Close'].pct_change()
    data = data.loc[data.index >= pd.to_datetime(start_date)].dropna()
    return data

def filter_and_rank_stocks(tickers, start_date, end_date, min_volume, min_price, max_price, min_sortino, min_diff_ratio, top_n):
    """종목 필터링 및 Sortino Ratio, Price Increase Ratio로 랭킹"""
    filtered_stocks = []

    for ticker in tickers:
        try:
            data = get_stock_data(ticker, start_date, end_date)
            if data.empty:
                logger.warning(f"No data for {ticker}")
                continue
            
            # 필터 조건
            if (data['Volume'].mean() < min_volume or
                data['Close'].iloc[-1] < min_price or
                data['Close'].iloc[-1] > max_price):
                continue

            # Sortino Ratio 계산
            sortino_ratio = calculate_sortino_ratio(data['Daily Return'])
            if sortino_ratio < min_sortino:
                continue

            # Price Increase Ratio 계산
            price_increase_ratio = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
            if price_increase_ratio < min_diff_ratio:
                continue

            filtered_stocks.append({
                "Ticker": ticker,
                "Sortino Ratio": sortino_ratio,
                "Price Increase Ratio": price_increase_ratio,
                "Combined Score": sortino_ratio + price_increase_ratio,
                "Price Range": f"{data['Close'].min():.2f} - {data['Close'].max():.2f}",
                "Last Close": data['Close'].iloc[-1],
                "Average Volume": data['Volume'].mean()
            })

        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")

    filtered_stocks.sort(key=lambda x: x['Combined Score'], reverse=True)
    return pd.DataFrame(filtered_stocks[:top_n])