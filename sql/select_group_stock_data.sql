select trade_date ,count(*) from stock_data
group by trade_date 
order by trade_date desc
limit 10;