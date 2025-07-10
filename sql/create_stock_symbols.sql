-- public.stock_symbols definition

-- Drop table

-- DROP TABLE public.stock_symbols;

CREATE TABLE public.stock_symbols (
	"no" serial4 NOT NULL,
	symbol text NULL,
	name text NULL,
	last_sale numeric NULL,
	market_cap numeric NULL,
	ipo_year int4 NULL,
	sector text NULL,
	industry text NULL,
	exchange text NULL,
	test_issue bool NULL,
	round_lot_size int4 NULL,
	etf bool NULL,
	market_category text NULL,
	financial_status text NULL,
	next_shares bool NULL,
	act_symbol text NULL,
	cqs_symbol text NULL,
	nasdaq_symbol text NULL,
	lastsale varchar(50) NULL,
	marketcap varchar(50) NULL,
	ipoyear varchar(50) NULL
);