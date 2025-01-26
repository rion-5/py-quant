import yfinance as yf
from psycopg2.extras import RealDictCursor
from data.database import get_connection
import pandas as pd

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
    select ticker,avg(volume) from stock_data
    where trade_date between %s and %s
    and volume >= %s
    and close_price between %s and %s
    group by ticker
    having count(*) >= (select count(distinct trade_date) from stock_data
                        where trade_date between %s and %s) - 2 
    limit %s;
    """
  try:
    with get_connection() as conn:
      with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query,(start_date,end_date,volume,min_price, max_price, start_date,end_date, top_n))
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

