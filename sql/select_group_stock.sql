select trading_date,count(*) from stock
group by trading_date 
order by trading_date desc
limit 10;