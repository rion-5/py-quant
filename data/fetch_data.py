from psycopg2.extras import RealDictCursor
from data.database import get_connection

def get_stock_data(symbol, start_date, end_date):
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

def get_recent_trading_days(days=14):
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

def get_stock_symbols():
  query="""
    select symbol,name, exchange, etf  from stock_symbols
    where exchange  IN ('NASDAQ','NYSE')
    and test_issue = false
    and financial_status <> 'Deficient'  ;
    """