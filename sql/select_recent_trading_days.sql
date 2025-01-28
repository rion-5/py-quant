--최근 저장된 거래일
select max(trading_date) from stock;

SELECT MIN(trading_date) AS start_date,
       MAX(trading_date) AS end_date
FROM (SELECT distinct trading_date
      FROM stock
      order BY trading_date DESC LIMIT 14);


