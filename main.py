from data.data_fetcher import fetch_symbols_from_db, fetch_momentum_symbols_from_db
from strategies.momentum import filter_and_rank_stocks

# 날짜 설정
start_date = "2025-01-15"
end_date = "2025-01-23"

# 조건 설정
min_volume = 8000000
min_price = 100
max_price = 1000
min_sortino = 0.2
min_diff_ratio = 0.2
top_n = 20

# 미국 주식 티커 가져오기 (예: NASDAQ, NYSE 종목)
def get_us_stock_tickers():
  return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]

    # symbols = fetch_symbols_from_db()
    # tickers = [ticker['symbol'] for ticker in symbols]
    # return tickers 
# 실행
if __name__ == "__main__":
    # tickers = get_us_stock_tickers()
    tickers =fetch_momentum_symbols_from_db(start_date, end_date, min_volume, min_price, max_price)
    # print(tickers)
    result = filter_and_rank_stocks(tickers, start_date, end_date, min_volume, min_price, max_price, min_sortino, min_diff_ratio, top_n)
    print(result)
