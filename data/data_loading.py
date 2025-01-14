from psycopg2.extras import RealDictCursor
from data.database import get_connection


def us_stock_holidays(year):
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

