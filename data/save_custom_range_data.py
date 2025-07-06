import data.data_fetcher as fetch
import data.data_saver as save
from data.trading_calendar import is_trading_day
from datetime import datetime, timedelta, date
import time
import argparse
from datetime import datetime

def validate_date(date_str):
    """
    날짜 문자열이 올바른 형식인지 확인합니다 (YYYY-MM-DD).
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")

def main():
    # ArgumentParser 초기화
    parser = argparse.ArgumentParser(
        description="Save stock data for a specific symbol and date range."
    )
    # 명령줄 인자 추가
    parser.add_argument(
        "start_date", type=validate_date, help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "end_date", type=validate_date, help="End date in YYYY-MM-DD format"
    )

    # 인자 파싱
    args = parser.parse_args()
    start_date = args.start_date.date();
    end_date = args.end_date.date()
    adjusted_end_date = end_date + timedelta(days=1)

    symbols = fetch.fetch_symbols_from_db()
    tickers = tuple(row['symbol'] for row in symbols)

    # 시작 시간 기록
    start_time = datetime.now()
    print(f"전체 데이터 개수 : {len(tickers)}")  # 전체 데이터 개수 출력

    # for symbol in tickers:
    for index, symbol in enumerate(tickers, start=1):  # enumerate로 번호와 데이터를 가져옴
      stock_data = fetch.fetch_stock_data_from_yfinance(symbol, start_date, adjusted_end_date)
      time.sleep(1.5)
      save.save_stock_data_in_db(stock_data)
      print(f"{index} {symbol} {start_date} {end_date} ")  # 현재 번호와 ticker 출력
    
    # 종료 시간 기록
    end_time = datetime.now()

    print(f"시작시간: {start_time.strftime("%Y-%m-%d %H:%M:%S")}")  # 시작 시간 출력    
    print(f"종료시간: {end_time.strftime("%Y-%m-%d %H:%M:%S")}")  # 종료 시간 출력
if __name__ == "__main__":
    main()
