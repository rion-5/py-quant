import yfinance as yf
from datetime import datetime, timedelta
from data.database import get_connection

def fetch_yesterday_stock_data(ticker):
    """
    Fetch yesterday's trading data for a given stock ticker using yfinance.

    Args:
        ticker (str): The stock ticker symbol (e.g., "TSLA").

    Returns:
        dict: A dictionary with the stock's trading data for yesterday, or None if no data is available.
    """
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    start_date = yesterday.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')  # 'end_date' is exclusive in yfinance

    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)

    if not data.empty:
        yesterday_data = data.iloc[0]
        return {
            "ticker": ticker,
            "date": start_date,
            "open": yesterday_data["Open"],
            "high": yesterday_data["High"],
            "low": yesterday_data["Low"],
            "close": yesterday_data["Close"],
            "volume": yesterday_data["Volume"]
        }
    else:
        print(f"No trading data available for {ticker} on {start_date}.")
        return None

def store_stock_data_to_db(data):
    """
    Store stock trading data into PostgreSQL.

    Args:
        data (dict): A dictionary containing stock trading data.
    """
    insert_query = """
    INSERT INTO stock_data (ticker, trade_date, open_price, high_price, low_price, close_price, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (ticker, trade_date) DO NOTHING;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(insert_query, (
                data["ticker"],
                data["date"],
                data["open"],
                data["high"],
                data["low"],
                data["close"],
                data["volume"]
            ))
        conn.commit()

def main():
    symbols = ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"]  # Replace with the actual list of symbols
    for ticker in symbols:
        print(f"Fetching data for {ticker}...")
        stock_data = fetch_yesterday_stock_data(ticker)
        if stock_data:
            print(f"Storing data for {ticker} into the database...")
            store_stock_data_to_db(stock_data)

if __name__ == "__main__":
    main()
