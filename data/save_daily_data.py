import data.data_fetcher as fetch
import data.data_saver as save
from data.trading_calendar import is_trading_day
from datetime import datetime, timedelta, date


# # 주말 및 공휴일 확인 함수
# def is_trading_day(date):
#     # 날짜를 datetime 객체로 변환 (필요시)
#     if isinstance(date, str):
#         date = datetime.strptime(date, '%Y-%m-%d').date()
    
#     # 요일 확인 (locale 설정에 따라 영어/한국어 처리 가능)
#     locale.setlocale(locale.LC_TIME, 'C')  # 'C'는 영어 요일 반환, 'ko_KR.UTF-8'은 한국어
#     weekday = date.strftime('%A')  # 'Monday', 'Tuesday' 등
    
#     if weekday in ["Saturday", "Sunday", "토요일", "일요일"]:
#         return False
    
#     # 연도 추출
#     year = date.year
    
#     # 연도별 주식 시장 공휴일 가져오기 (사용자 정의 함수 필요)
#     holidays = dl.us_stock_holidays(year)  # 연도별 공휴일 반환 함수
#     holiday_dates = [holiday[0] for holiday in holidays]  # 공휴일 리스트
    
#     # 거래일 여부 반환
#     return date not in holiday_dates

def main():
  # aapl = fetch.get_stock_data('AAPL','2025-01-01','2025-01-08')
  # print(aapl)

  # [(start_date, end_date)] = fetch.get_recent_trading_days()
  # start_date = start_date.strftime("%Y-%m-%d")
  # end_date = end_date.strftime("%Y-%m-%d")
  
  today = date.today()
  yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')

  if (is_trading_day(yesterday)):
    symbols = fetch.fetch_symbols_from_db()
    tickers = tuple(row['symbol'] for row in symbols)

    # 시작 시간 기록
    start_time = datetime.now()
    print(f"전체 데이터 개수 : {len(tickers)}")  # 전체 데이터 개수 출력

    # for symbol in tickers:
    for index, symbol in enumerate(tickers, start=1):  # enumerate로 번호와 데이터를 가져옴
      stock_data = fetch.fetch_stock_data_from_yfinance(symbol, yesterday, today)
      save.save_stock_data_in_db(stock_data)
      print(f"{index} {symbol}")  # 현재 번호와 ticker 출력
    
    # 종료 시간 기록
    end_time = datetime.now()

    print(f"시작시간: {start_time.strftime("%Y-%m-%d %H:%M:%S")}")  # 시작 시간 출력    
    print(f"종료시간: {end_time.strftime("%Y-%m-%d %H:%M:%S")}")  # 종료 시간 출력

if __name__ == '__main__':
  main()