from data.database import get_connection

def save_stock_data_in_db(stock_data):
    """
    Store stock trading data into PostgreSQL with error handling.

    Args:
        stock_data (dict): A dictionary containing stock trading data.
    """
    insert_query = """
    INSERT INTO stock_data (ticker, trade_date, open_price, high_price, low_price, close_price, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (ticker, trade_date) DO NOTHING;
    """
    conn = None
    try:
        # Get database connection
        conn = get_connection()
        with conn.cursor() as cur:
            for record in stock_data:
              try:
                cur.execute(insert_query, (
                  record["ticker"],
                  record["trade_date"],
                  record["open"],
                  record["high"],
                  record["low"],
                  record["close"],
                  record["volume"]
                ))
              except Exception as e:
                print(f"Error saving stock data: {e}") 
                continue     
            conn.commit()  # Commit changes if no exception occurs

    except Exception as e:
      if conn:
        conn.rollback()  # Rollback changes on error
        print(f"Error saving stock data: {e}")
        raise  # Re-raise the exception after logging
    finally:
      if conn:
        conn.close()  # Ensure connection is closed
