import yfinance as yf
import pandas as pd
from strategies.sortino_ratio import calculate_sortino_ratio
from strategies.filters import apply_filters
from data.data_fetcher import fetch_stock_data_from_db
from datetime import datetime, timedelta, date


# 데이터 가져오기
def get_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    new_date_str = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=3)).strftime('%Y-%m-%d')
    # data = fetch_stock_data_from_db(ticker, new_date_str, end_date)
    data['Daily Return'] = data['Close'].pct_change()

    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    data = data[data['Trade_date'] >= start_date_obj].dropna()
    # print(data)
    return data

# 종목 필터링 및 랭킹
def filter_and_rank_stocks(tickers, start_date, end_date, min_volume, min_price, max_price, min_sortino, min_diff_ratio, top_n):
    filtered_stocks = []

    for ticker in tickers:
        try:
            data = get_stock_data(ticker, start_date, end_date)
            # print(data)
            # 필터 조건 적용
            # if not apply_filters(data, min_volume, min_price, max_price, min_diff_ratio):
            #     continue

            # Sortino Ratio 계산
            sortino_ratio = calculate_sortino_ratio(data['Daily Return'])
            
            if sortino_ratio < min_sortino:
                continue

            # 주가 상승율 계산
            price_increase_ratio = float((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0])
            # print(f"{ticker} {sortino_ratio} {price_increase_ratio}")
            filtered_stocks.append({
                "Ticker": ticker,
                "Sortino Ratio": sortino_ratio,
                "Price Increase Ratio": price_increase_ratio,
                # "Combined Score": sortino_ratio * 0.7 + price_increase_ratio * 0.3,
                "Combined Score": sortino_ratio * 0.3 + price_increase_ratio * 0.7,

                "Price Range": f"{data['Close'].min():.2f} - {data['Close'].max():.2f}",
                "Average Volume": data['Volume'].mean()
            })

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    # 정렬: Combined Score 기준 내림차순
    filtered_stocks.sort(key=lambda x: x['Combined Score'], reverse=True)
    return pd.DataFrame(filtered_stocks[:top_n])
