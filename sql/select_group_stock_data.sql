select trade_date ,count(*) from stock_data
group by trade_date 
order by trade_date desc
--limit 10
;

-- delete from stock_data where trade_date='2025-07-02';


delete from stock_data
where trade_date in
(
	with trade_count as (
	  select trade_date ,count(*) as count from stock_data
	  group by trade_date 
	  order by trade_date desc
	)
	select trade_date from trade_count
	where count < 6600
);

