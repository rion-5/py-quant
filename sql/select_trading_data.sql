SELECT trading_date, symbol, adjusted, volume
FROM stock
WHERE symbol = :symbol
  AND trading_date >= :start_date 
  AND trading_date <= :end_date;
