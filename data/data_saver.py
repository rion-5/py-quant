from data.database import get_connection

def save_stock_data_in_db(stock_data):
    """
    Store stock trading data into PostgreSQL with error handling.

    Args:
        stock_data (dict): A dictionary containing stock trading data.
    """

    insert_query = """
    INSERT INTO stock_data (ticker, trade_date, open_price, high_price, low_price, close_price, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    # ON CONFLICT (ticker, trade_date) DO NOTHING
    conn = None
    try:
      # Get database connection
      conn = get_connection()
      with conn.cursor() as cur:
          for index, record in enumerate(stock_data, start=1):  # enumerate로 번호와 데이터를 가져옴
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

def save_stock_info_in_db(stock_info):
    """
    Store stock basic information into PostgreSQL with error handling.

    Args:
        stock_info (dict): A dictionary containing stock basic information.
    """

    insert_query = """
    INSERT INTO stock_info (ticker, company_name, industry, sector, market_cap, currency)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (ticker) DO UPDATE 
    SET company_name = EXCLUDED.company_name,
        industry = EXCLUDED.industry,
        sector = EXCLUDED.sector,
        market_cap = EXCLUDED.market_cap,
        currency = EXCLUDED.currency;
    """
    
    conn = None
    try:
        # Get database connection
        conn = get_connection()
        with conn.cursor() as cur:
            try:
                cur.execute(insert_query, (
                    stock_info["ticker"],
                    stock_info["company_name"],
                    stock_info["industry"],
                    stock_info["sector"],
                    stock_info["market_cap"],
                    stock_info["currency"]
                ))
            except Exception as e:
                print(f"Error saving stock info: {e}")
                return  # 에러 발생 시 종료
            
            conn.commit()  # 커밋하여 변경사항 저장

    except Exception as e:
        if conn:
            conn.rollback()  # 오류 발생 시 롤백
            print(f"Database error: {e}")
            raise  # 예외 재발생
    finally:
        if conn:
            conn.close()  # 연결 닫기


def save_stock_financials_in_db(financials_data):
    """
    Store stock financials history into PostgreSQL.

    Args:
        financials_data (dict): A dictionary of financials history.
    """
    insert_query = """
    INSERT INTO stock_financials_history (
        ticker, recorded_at, trailing_pe, forward_pe, book_value, 
        price_to_book, earnings_growth, revenue_growth, 
        return_on_assets, return_on_equity, debt_to_equity
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (ticker, recorded_at) DO NOTHING;
    """

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(insert_query, (
                financials_data["ticker"],
                financials_data["recorded_at"],
                financials_data["trailing_pe"],
                financials_data["forward_pe"],
                financials_data["book_value"],
                financials_data["price_to_book"],
                financials_data["earnings_growth"],
                financials_data["revenue_growth"],
                financials_data["return_on_assets"],
                financials_data["return_on_equity"],
                financials_data["debt_to_equity"]
            ))
        conn.commit()  # 변경 사항 적용

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error while saving {financials_data['ticker']}: {e}")
        raise
    finally:
        if conn:
            conn.close()