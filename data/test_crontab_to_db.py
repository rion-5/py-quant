import data.data_fetcher as fetch
import data.data_saver as save
from data.trading_calendar import is_trading_day
from datetime import datetime, timedelta, date

def main():
  stock_data = fetch.fetch_stock_data_from_yfinance('TSLA', '2024-12-04', '2024-12-05')
  save.save_stock_data_in_db(stock_data)

if __name__ == '__main__':
  main()