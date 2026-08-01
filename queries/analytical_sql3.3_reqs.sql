--Latest prices per market
SELECT MAX(date) as mdate, market, price
FROM raw_food_prices
GROUP BY market, price
ORDER BY mdate;

SELECT commodity, 
ROUND(AVG(price),2) AS average_price, 
MIN(price) AS minimum_price,
MAX(price) AS maximum_price
FROM raw_food_prices
GROUP BY commodity;

SELECT commodity, 
COUNT(market) AS market_count
FROM raw_food_prices
GROUP BY commodity
HAVING COUNT(market)>10;

SELECT EXTRACT(year from date) AS price_year,
COUNT(commodity) AS commodities_sold
FROM raw_food_prices
GROUP BY price_year
ORDER BY price_year;