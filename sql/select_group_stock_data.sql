select trade_date ,count(*) from stock_data
group by trade_date 
order by trade_date desc
limit 10;

delete from stock_data where trade_date='2025-07-02';