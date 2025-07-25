    -- SELECT 
    --     ticker,
    --     trade_date,
    --     open_price,
    --     high_price,
    --     low_price,
    --     close_price,
    --     volume
    -- FROM stock_data
    -- WHERE trade_date BETWEEN '2025-01-01' AND '2025-01-21'
    --   AND volume >= 8000000
    --   AND close_price BETWEEN 100 AND 1000
    -- GROUP BY ticker, trade_date, open_price, high_price, low_price, close_price, volume


-- select * from stock_data
-- WHERE ticker='NVDA'
-- and trade_date BETWEEN '2025-01-01' AND '2025-01-28';

WITH last_trading_day AS (
    SELECT MAX(trade_date) AS trade_date
    FROM stock_data
    WHERE trade_date <= '2025-01-20'
    AND trade_date NOT IN (SELECT holiday_date FROM market_holidays)
    AND EXTRACT(DOW FROM trade_date) NOT IN (0, 6)
)
SELECT ticker, COUNT(*) 
FROM stock_data 
WHERE ticker IN (
    SELECT ticker 
    FROM stock_data
    WHERE trade_date = (SELECT trade_date FROM last_trading_day)
    AND close_price BETWEEN 100 AND 1000
)
AND trade_date BETWEEN '2024-01-02' AND '2025-01-22' 
AND volume >= 5000000
GROUP BY ticker
HAVING COUNT(*) >= (
    SELECT COUNT(DISTINCT trade_date) FROM stock_data 
    WHERE trade_date BETWEEN '2024-01-02' AND '2025-01-22'
) - (
    SELECT COUNT(DISTINCT trade_date) FROM stock_data 
    WHERE trade_date BETWEEN '2024-01-02' AND '2025-01-22'
) / 15
LIMIT 50;
;
-- delete FROM stock_data_2024 WHERE trade_date >= '2025-01-01';