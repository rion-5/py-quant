select ticker, count(*) from stock_data where trade_date between '2024-07-02' and '2025-01-22' 
and close_price between 100 and 1000 and volume >= 5000000
group by ticker
having count(*) >= (select count(distinct trade_date) from stock_data where trade_date between '2024-07-02' and '2025-01-22')-
(select count(distinct trade_date) from stock_data where trade_date between '2024-07-02' and '2025-01-22')/15
LIMIT 50
;
--
--select days / 15 from (values(19),(98),(60) )as temp(days) ;
--
--select '2024-07-01' as start_date, '2024-12-31' as end_date, 100 as min_price, 1000 as max_price, 5000000 as min_volume;

