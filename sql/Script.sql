-- 조건: 최근 15일 거래일간 조정종가(adjusted)가 100~1000달러이면서 거래량이 8000000 이상이 13회 이상인 종목
WITH DateRange AS (
  SELECT MIN(trading_date) AS start_date,
         MAX(trading_date) AS end_date
  FROM (SELECT DISTINCT trading_date
        FROM stock
        ORDER BY trading_date DESC LIMIT 15)
)
select symbol, count(*),
		round(min(adjusted)::numeric,2) as min_adjusted,
		round(avg(adjusted)::numeric,2) as avg_adjusted,
		round(max(adjusted)::numeric,2) as max_adjusted,
		round(min(volume)::numeric,0) as min_volume,
		round(max(volume)::numeric,0) as max_volume
FROM stock
WHERE trading_date BETWEEN (SELECT start_date FROM DateRange)
                      AND (SELECT end_date FROM DateRange)
and adjusted between 100 and 1000
and volume >= 8000000
group by symbol
having count(*) >= 13
order by min_volume desc;