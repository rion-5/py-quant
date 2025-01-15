import yfinance as yf
from datetime import datetime, timedelta
from data.database import get_connection
from data.trading_calendar import is_trading_day

def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetch stock trading data for a given ticker and date range.

    Args:
        ticker (str): The stock ticker symbol (e.g., "TSLA").
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        list[dict]: A list of dictionaries with trading data for each day.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)

    if not data.empty:
        results = []
        for date, row in data.iterrows():
            results.append({
                # "ticker": ticker,
                # "date": date.strftime('%Y-%m-%d'),
                # "open": row["Open"],
                # "high": row["High"],
                # "low": row["Low"],
                # "close": row["Close"],
                # "volume": row["Volume"]
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
        print(f"No data available for {ticker} between {start_date} and {end_date}.")
        return []

def store_stock_data_to_db(data):
    """
    Store stock trading data into PostgreSQL.

    Args:
        data (list[dict]): A list of dictionaries containing stock trading data.
    """
    if not data:
        print("No data to store.")
        return

    insert_query = """
    INSERT INTO stock_data (ticker, trade_date, open_price, high_price, low_price, close_price, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (ticker, trade_date) DO NOTHING;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for record in data:
                cur.execute(insert_query, (
                    record["ticker"],
                    record["date"],
                    record["open"],
                    record["high"],
                    record["low"],
                    record["close"],
                    record["volume"]
                ))
        conn.commit()

def fetch_and_store_ticker_data(ticker, start_date=None, end_date=None):
    """
    Fetch and store stock trading data for a given ticker and date range.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): Optional start date in 'YYYY-MM-DD' format. Defaults to 1 day before today.
        end_date (str): Optional end date in 'YYYY-MM-DD' format. Defaults to today.
    """
    today = datetime.now().date()
    start_date = start_date or (today - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = end_date or today.strftime('%Y-%m-%d')

    # Fetch trading days only
    all_dates = [start_date + timedelta(days=i) for i in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)]
    trading_days = [d.strftime('%Y-%m-%d') for d in all_dates if is_trading_day(d)]

    for trading_day in trading_days:
        print(f"Fetching data for {ticker} on {trading_day}...")
        stock_data = fetch_stock_data(ticker, trading_day, trading_day)
        store_stock_data_to_db(stock_data)
