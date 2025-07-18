import data.data_fetcher as fetch
import data.data_saver as save
from data.trading_calendar import is_trading_day
from datetime import datetime, timedelta, date
import time

def main():

  today = date.today()
  yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')

  if (is_trading_day(yesterday)):
    symbols = fetch.fetch_symbols_from_db()
    tickers = tuple(row['symbol'] for row in symbols)

    # 시작 시간 기록
    start_time = datetime.now()

    # for symbol in tickers:
    for index, symbol in enumerate(tickers, start=1):  # enumerate로 번호와 데이터를 가져옴
      stock_data = fetch.fetch_stock_data_from_yfinance(symbol, yesterday, today)
      time.sleep(1.5)
      if stock_data:
        save.save_stock_data_in_db(stock_data)
        print(f"{index}/{len(tickers)} {symbol} 저장 완료")
      else:
        print(f"{index}/{len(tickers)} {symbol} 정보 없음")
    
    # 종료 시간 기록
    end_time = datetime.now()

    print(f"전체 종목 수 : {len(tickers)}")  # 전체 데이터 개수 출력
    print(f"시작시간: {start_time.strftime("%Y-%m-%d %H:%M:%S")}")  # 시작 시간 출력    
    print(f"종료시간: {end_time.strftime("%Y-%m-%d %H:%M:%S")}")  # 종료 시간 출력

if __name__ == '__main__':
  main()
