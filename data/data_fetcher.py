# data/data_fetcher.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from psycopg2.extras import RealDictCursor
from data.database import get_connection
from functools import lru_cache
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_stock_data_from_db(symbol, start_date, end_date):
    if not isinstance(start_date, (str, datetime)) or not isinstance(end_date, (str, datetime)):
        raise ValueError("start_date and end_date must be strings or datetime objects")
    if isinstance(start_date, datetime):
        start_date = start_date.strftime('%Y-%m-%d')
    if isinstance(end_date, datetime):
        end_date = end_date.strftime('%Y-%m-%d')
    
    query = """
    SELECT trade_date as Trade_date,
           open_price as Open,
           high_price as High,
           low_price as Low,
           close_price as Close,
           volume as Volume
    FROM stock_data
    WHERE ticker = %s AND trade_date BETWEEN %s AND %s;
    """
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (symbol, start_date, end_date))
                rows = cur.fetchall()
                if not rows:
                    logger.info(f"No data found for {symbol} between {start_date} and {end_date}")
                    return pd.DataFrame(columns=['Trade_date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                data = pd.DataFrame(rows)
                data.columns = [col.capitalize() for col in data.columns]
                data['Trade_date'] = pd.to_datetime(data['Trade_date'])
                data.set_index('Trade_date', inplace=True)
                return data
    except Exception as e:
        logger.error(f"Query Execution error for {symbol}: {e}")
        return pd.DataFrame(columns=['Trade_date', 'Open', 'High', 'Low', 'Close', 'Volume'])

def fetch_holidays_from_db(year):
    query = """
        SELECT holiday_date
        FROM market_holidays
        WHERE holiday_date BETWEEN %s AND %s;
    """
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (start_date, end_date))
                holidays = [row[0] for row in cur.fetchall()]
                return holidays if holidays else []
    except Exception as e:
        logger.error(f"Query Execution error: {e}")
        return []

def fetch_recent_trading_days_from_db(days=14):
    query = """
        SELECT MIN(trade_date) AS start_date,
               MAX(trade_date) AS end_date
        FROM (
            SELECT DISTINCT trade_date
            FROM stock_data
            WHERE trade_date NOT IN (SELECT holiday_date FROM market_holidays)
            AND EXTRACT(DOW FROM trade_date) NOT IN (0, 6)
            ORDER BY trade_date DESC
            LIMIT %s
        ) sub;
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (days,))
                result = cur.fetchone()
                return {"start_date": result[0], "end_date": result[1]} if result else {}
    except Exception as e:
        logger.error(f"Query Execution error: {e}")
        return {}

@lru_cache(maxsize=100)
def fetch_stock_data_from_yfinance(ticker, start_date, end_date):
    if not isinstance(start_date, (str, datetime)) or not isinstance(end_date, (str, datetime)):
        raise ValueError("start_date and end_date must be strings or datetime objects")
    if isinstance(start_date, datetime):
        start_date = start_date.strftime('%Y-%m-%d')
    if isinstance(end_date, datetime):
        end_date = end_date.strftime('%Y-%m-%d')
    
    try:
        data = yf.Ticker(ticker).history(start=start_date, end=end_date)
        if data.empty:
            logger.info(f"No data available for {ticker} between {start_date} and {end_date}")
            return pd.DataFrame()
        data = data.dropna()
        data = data.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]
        data.columns = ['Trade_date', 'Open', 'High', 'Low', 'Close', 'Volume']
        data['Trade_date'] = pd.to_datetime(data['Trade_date'])
        data.set_index('Trade_date', inplace=True)
        return data
    except Exception as e:
        logger.error(f"Unexpected error for {ticker}: {e}")
        return pd.DataFrame()

def fetch_symbols_from_db():
    query = """
        SELECT symbol, name, exchange, etf FROM stock_symbols
        WHERE exchange IN ('NASDAQ', 'NYSE')
        AND test_issue = FALSE
        AND financial_status <> 'Deficient';
    """
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return pd.DataFrame(rows) if rows else pd.DataFrame(columns=['symbol', 'name', 'exchange', 'etf'])
    except Exception as e:
        logger.error(f"Query Execution error: {e}")
        return pd.DataFrame(columns=['symbol', 'name', 'exchange', 'etf'])

def fetch_momentum_symbols_from_db(start_date, end_date, volume, min_price, max_price, top_n):
    query = """
        WITH last_trading_day AS (
            SELECT MAX(trade_date) AS trade_date
            FROM stock_data
            WHERE trade_date <= %s
            AND trade_date NOT IN (SELECT holiday_date FROM market_holidays)
            AND EXTRACT(DOW FROM trade_date) NOT IN (0, 6)
        )
        SELECT ticker, AVG(volume) AS avg_volume
        FROM stock_data
        WHERE ticker IN (
            SELECT ticker 
            FROM stock_data
            WHERE trade_date = (SELECT trade_date FROM last_trading_day)
            AND close_price BETWEEN %s AND %s
        )
        AND trade_date BETWEEN %s AND %s
        AND volume >= %s
        GROUP BY ticker
        HAVING COUNT(*) >= (SELECT COUNT(DISTINCT trade_date) * 0.9 FROM stock_data
                           WHERE trade_date BETWEEN %s AND %s)
        ORDER BY avg_volume DESC
        LIMIT %s;
    """
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (end_date, min_price, max_price, start_date, end_date, volume, start_date, end_date, top_n))
                rows = cur.fetchall()
                df = pd.DataFrame(rows)
                return tuple(df['ticker']) if not df.empty else ()
    except Exception as e:
        logger.error(f"Query Execution error: {e}")
        return ()

@lru_cache(maxsize=100)
def fetch_stock_info_from_yfinance(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            logger.info(f"No info available for {ticker}")
            return {}
        return {
            "ticker": ticker,
            "company_name": info.get("longName", "N/A"),
            "industry": info.get("industry", "N/A"),
            "sector": info.get("sector", "N/A"),
            "market_cap": info.get("marketCap", None),
            "currency": info.get("currency", "N/A"),
        }
    except Exception as e:
        logger.error(f"Unexpected error for {ticker}: {e}")
        return {}

@lru_cache(maxsize=100)
def fetch_stock_financials_from_yfinance(ticker):
    try:
        stock = yf.Ticker(ticker)
        stats = stock.info
        if not stats:
            logger.info(f"No financials available for {ticker}")
            return {}
        return {
            "ticker": ticker,
            "recorded_at": datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d'),
            "trailing_pe": stats.get("trailingPE", None),
            "forward_pe": stats.get("forwardPE", None),
            "book_value": stats.get("bookValue", None),
            "price_to_book": stats.get("priceToBook", None),
            "earnings_growth": stats.get("earningsGrowth", None),
            "revenue_growth": stats.get("revenueGrowth", None),
            "return_on_assets": stats.get("returnOnAssets", None),
            "return_on_equity": stats.get("returnOnEquity", None),
            "debt_to_equity": stats.get("debtToEquity", None)
        }
    except Exception as e:
        logger.error(f"Error fetching financials for {ticker}: {e}")
        return {}

def compute_rsi(series, period=14):
    try:
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        if rs.isna().any():
            logger.warning("RSI calculation resulted in NaN")
            return None
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return None

@lru_cache(maxsize=100)
def get_momentum_indicators(ticker):
    try:
        end_date = datetime.now(pytz.timezone('Asia/Seoul'))
        start_date = end_date - timedelta(days=365)
        data = fetch_stock_data_from_db(ticker, start_date, end_date)
        if data.empty:
            data = fetch_stock_data_from_yfinance(ticker, start_date, end_date)
        if data.empty:
            logger.info(f"No data for {ticker}")
            return {}
        
        rsi = compute_rsi(data['Close'])
        high_52w_ratio = data['Close'].iloc[-1] / data['Close'].max() if not data['Close'].empty else None
        ma_60 = data['Close'].rolling(window=60, min_periods=1).mean().iloc[-1] if len(data) >= 1 else None
        ma_200 = data['Close'].rolling(window=200, min_periods=1).mean().iloc[-1] if len(data) >= 1 else None
        change_1m = None if len(data) < 22 else (data['Close'].iloc[-1] - data['Close'].iloc[-22]) / data['Close'].iloc[-22] * 100
        change_3m = None if len(data) < 66 else (data['Close'].iloc[-1] - data['Close'].iloc[-66]) / data['Close'].iloc[-66] * 100
        change_6m = None if len(data) < 132 else (data['Close'].iloc[-1] - data['Close'].iloc[-132]) / data['Close'].iloc[-132] * 100
        change_1y = None if len(data) < 1 else (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0] * 100
        
        return {
            "RSI": rsi,
            "52W High Ratio": high_52w_ratio,
            "60-Day MA": ma_60,
            "200-Day MA": ma_200,
            "1M Change": change_1m,
            "3M Change": change_3m,
            "6M Change": change_6m,
            "1Y Change": change_1y
        }
    except Exception as e:
        logger.error(f"Error fetching momentum indicators for {ticker}: {e}")
        return {}

@lru_cache(maxsize=100)
def get_value_indicators(ticker):
    try:
        financials = fetch_stock_financials_from_yfinance(ticker)
        if not financials:
            return {}
        return {
            "PER": financials.get('trailing_pe', None),
            "PBR": financials.get('price_to_book', None),
            "EPS": financials.get('trailing_eps', None),
            "ROE": financials.get('return_on_equity', None),
            "Revenue Growth": financials.get('revenue_growth', None),
            "Debt to Equity": financials.get('debt_to_equity', None)
        }
    except Exception as e:
        logger.error(f"Error fetching value indicators for {ticker}: {e}")
        return {}