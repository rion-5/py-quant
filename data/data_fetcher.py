import yfinance as yf
from psycopg2.extras import RealDictCursor
from data.database import get_connection
import pandas as pd
from datetime import date

def fetch_stock_data_from_db(symbol, start_date, end_date):
  query = """
  SELECT trade_date as Trade_date,
         open_price as Open,
         high_price as High,
         low_price as Low ,
         close_price as Close, 
         volume as Volume
  FROM stock_data
  WHERE ticker = %s AND trade_date BETWEEN %s AND %s;
  """
  try:
    with get_connection() as conn:
      with conn.cursor(cursor_factory = RealDictCursor) as cur:
        cur.execute(query, (symbol, start_date, end_date))
        rows = cur.fetchall()
        data = pd.DataFrame(rows)
        # Ensure column names' first letter remains capitalized
        data.columns = [col.capitalize() for col in data.columns]
        return data
  except Exception as e:
    print(f"Query Execution error: {e}")
    return None
  finally:
    if conn:
      conn.close()

def fetch_holidays_from_db(year):
    query = """
        SELECT holiday_date
        FROM market_holidays
        WHERE EXTRACT(YEAR FROM holiday_date) = %s ;
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (year,))
                return cur.fetchall()
    except Exception as e:
        print(f"Query Execution error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def fetch_recent_trading_days_from_db(days=14):
  query = """
    SELECT MIN(trade_date) AS start_date,
           MAX(trade_date) AS end_date
    FROM (SELECT distinct trade_date
          FROM stock_data
          ORDER BY trade_date DESC LIMIT %s);
    """
  try:
    with get_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(query,(days,))
        return cur.fetchall()
  except Exception as e:
    print(f"Query Execution error: {e}")
    return None
  finally:
    if conn:
      conn.close()



def fetch_stock_data_from_yfinance(ticker, start_date, end_date):
    """
    Fetch stock trading data for a given ticker and date range.

    Args:
        ticker (str): The stock ticker symbol (e.g., "TSLA").
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        list[dict]: A list of dictionaries with trading data for each day.
    """ 
    try:
      data = yf.Ticker(ticker).history(start=start_date, end=end_date, period=None)
    except Exception as e:
      data = pd.DataFrame()
      print(f"Unexpected error for {ticker}: {e}")
      
    if not data.empty:
        results = []
        for date, row in data.iterrows():
            results.append({
                "ticker": ticker,
                "trade_date": date.strftime('%Y-%m-%d'),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"])
            })
        return results
    else:
        #print(f"No data available for {ticker} between {start_date} and {end_date}.")
        return []


def fetch_stock_data_from_yf_download(ticker, start_date, end_date):
  download_data = yf.download(ticker, start=start_date,end=end_date, progress=False)
  data = download_data.xs(ticker, axis=1, level=1)
  return data

def fetch_symbols_from_db():
  query="""
    select symbol,name, exchange, etf  from stock_symbols
    where exchange  IN ('NASDAQ','NYSE')
    and test_issue = false
    and financial_status <> 'Deficient'  ;
    """
  try:
    with get_connection() as conn:
      with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()
  except Exception as e:
    print(f"Query Execution error: {e}")
    return None
  finally:
    if conn:
      conn.close()

def fetch_momentum_symbols_from_db(start_date, end_date, volume, min_price, max_price, top_n):
  query="""
    WITH last_trading_day AS (
    SELECT MAX(trade_date) AS trade_date
    FROM stock_data
    WHERE trade_date <= %s
    AND trade_date NOT IN (SELECT holiday_date FROM market_holidays)
    AND EXTRACT(DOW FROM trade_date) NOT IN (0, 6)
    )
    select ticker,avg(volume) from stock_data
    WHERE ticker IN (
    SELECT ticker 
    FROM stock_data
    WHERE trade_date = (SELECT trade_date FROM last_trading_day)
    AND close_price BETWEEN %s AND %s
    )
    and trade_date between %s and %s
    and volume >= %s
    group by ticker
    having count(*) >= (select count(distinct trade_date) from stock_data
                        where trade_date between %s and %s) - (select count(distinct trade_date) from stock_data
                        where trade_date between %s and %s)/14 
    limit %s;
    """
  try:
    with get_connection() as conn:
      with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query,(end_date, min_price, max_price, start_date,end_date,volume, start_date,end_date,start_date,end_date, top_n))
        rows = cur.fetchall()
        # Convert query result to a DataFrame
        df = pd.DataFrame(rows)
        # Return 'ticker' column as a tuple
        return tuple(df['ticker'])
  except Exception as e:
    print(f"Query Execution error: {e}")
    return None
  finally:
    if conn:
      conn.close()

def fetch_stock_info_from_yfinance(ticker):
    """
    Fetch basic stock information for a given ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., "TSLA").

    Returns:
        dict: A dictionary with basic stock information.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info  # yfinance의 기본 정보 가져오기

        return {
            "ticker": ticker,
            "company_name": info.get("longName", "N/A"),
            "industry": info.get("industry", "N/A"),
            "sector": info.get("sector", "N/A"),
            "market_cap": info.get("marketCap", None),
            "currency": info.get("currency", "N/A"),
        }
    except Exception as e:
        print(f"Unexpected error for {ticker}: {e}")
        return {}

def fetch_stock_financials_from_yfinance(ticker):
    """
    Fetch stock financials history for a given ticker from yfinance.

    Args:
        ticker (str): The stock ticker symbol (e.g., "AAPL").

    Returns:
        dict: A dictionary containing financials history.
    """
    try:
        stock = yf.Ticker(ticker)
        stats = stock.info  # yfinance의 info 딕셔너리에서 주요 지표 추출
    except Exception as e:
        print(f"Error fetching financials for {ticker}: {e}")
        return None

    financials_data = {
        "ticker": ticker,
        "recorded_at": date.today().strftime('%Y-%m-%d'),  # 오늘 날짜 기준
        "trailing_pe": stats.get("trailingPE"),
        "forward_pe": stats.get("forwardPE"),
        "book_value": stats.get("bookValue"),
        "price_to_book": stats.get("priceToBook"),
        "earnings_growth": stats.get("earningsGrowth"),
        "revenue_growth": stats.get("revenueGrowth"),
        "return_on_assets": stats.get("returnOnAssets"),
        "return_on_equity": stats.get("returnOnEquity"),
        "debt_to_equity": stats.get("debtToEquity")
    }

    return financials_data
