import data.data_fetcher as fetch
import data.data_saver as save
from data.trading_calendar import is_trading_day
from datetime import datetime, timedelta, date

def main():
    symbols = fetch.fetch_symbols_from_db()
    tickers = tuple(row['symbol'] for row in symbols)

    # 시작 시간 기록
    start_time = datetime.now()
    print(f"전체 종목 수: {len(tickers)}")

    # 종목별 stock_info 가져와서 저장
    for index, symbol in enumerate(tickers, start=1):
        try:
            stock_info = fetch.fetch_stock_info_from_yfinance(symbol)
            if stock_info:  # 데이터가 비어있지 않을 때만 저장
                save.save_stock_info_in_db(stock_info)
                print(f"{index}/{len(tickers)} {symbol} 저장 완료")
            else:
                print(f"{index}/{len(tickers)} {symbol} 정보 없음")
        except Exception as e:
            print(f"오류 발생: {symbol}, {e}")

    # 종료 시간 기록
    end_time = datetime.now()

    print(f"시작시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"종료시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
