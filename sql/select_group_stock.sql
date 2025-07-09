select trading_date,count(*) from stock
group by trading_date 
order by trading_date desc
limit 10;

delete from stock
where trading_date in
(
	with trade_count as (
	  select trading_date ,count(*) as count from stock
	  group by trading_date 
	  order by trading_date desc
	)
	select trading_date from trade_count
	where count < 6600
);