from data.data_fetcher import fetch_stock_data_from_yfinance,fetch_recent_trading_days_from_db

def main():
  aapl = fetch_stock_data_from_yfinance('AAPL','2025-01-01','2025-01-08')
  print(aapl)

  [(start_date, end_date)] = fetch_recent_trading_days_from_db()
  print(start_date)
  print(end_date)

if __name__ == '__main__':
  main()