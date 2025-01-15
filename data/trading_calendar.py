import locale
from datetime import datetime
import data.holiday_data_fetcher as dl

# def us_stock_holidays(year):
#     """
#     Returns the list of U.S. stock market holidays for a given year.

#     Args:
#         year (int): The year to retrieve holidays for.

#     Returns:
#         list[str]: A list of holiday dates in 'YYYY-MM-DD' format.
#     """
#     # 예제: 실제 구현에서는 API나 라이브러리를 사용하여 공휴일 데이터를 가져와야 합니다.
#     return [
#         f"{year}-01-01",  # New Year's Day
#         f"{year}-07-04",  # Independence Day
#         f"{year}-12-25",  # Christmas
#         # 추가 공휴일을 추가하세요.
#     ]

def is_trading_day(date):
    """
    Check if the given date is a trading day.

    Args:
        date (str or datetime): The date to check.

    Returns:
        bool: True if the date is a trading day, False otherwise.
    """
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()

    # Check if the date is a weekend
    if date.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
        return False

    # Check if the date is a U.S. stock market holiday
    year = date.year
    holidays = dl.us_stock_holidays(year)
    holiday_dates = [holiday[0] for holiday in holidays]  # 공휴일 리스트

    #return date.strftime('%Y-%m-%d') not in holidays
    return date not in holiday_dates