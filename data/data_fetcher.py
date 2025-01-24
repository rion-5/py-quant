import yfinance as yf
from psycopg2.extras import RealDictCursor
from data.database import get_connection
import pandas as pd

def fetch_stock_data_from_db(symbol, start_date, end_date):
  query = """
  SELECT trading_date, close, volume
  FROM stock
  WHERE symbol = %s AND trading_date BETWEEN %s AND %s;
  """
  try:
    with get_connection() as conn:
      with conn.cursor(cursor_factory = RealDictCursor) as cur:
        cur.execute(query, (symbol, start_date, end_date))
        return cur.fetchall()
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
    SELECT MIN(trading_date) AS start_date,
           MAX(trading_date) AS end_date
    FROM (SELECT distinct trading_date
          FROM stock
          ORDER BY trading_date DESC LIMIT %s);
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

def fetch_momentum_symbols_from_db(start_date, end_date, volume):
  query="""
    select ticker, count(*) from stock_data
    where trade_date between %s and %s
    and volume >= %s
    group by ticker
    having count(*) >= (select count(distinct trade_date) from stock_data
                        where trade_date between %s and %s) - 2 ;
    """
  try:
    with get_connection() as conn:
      with conn.cursor(cursor_factory=RealDictCursor) as cur:
       cur.execute(query,(start_date,end_date,volume,start_date,end_date))
       return cur.fetchall()
  except Exception as e:
    print(f"Query Execution error: {e}")
    return None
  finally:
    if conn:
      conn.close()

