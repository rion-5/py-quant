from data.data_fetcher import get_stock_data, get_recent_trading_days

def main():
  aapl = get_stock_data('AAPL','2025-01-01','2025-01-08')
  print(aapl)

  [(start_date, end_date)] = get_recent_trading_days()
  print(start_date)
  

if __name__ == '__main__':
  main()