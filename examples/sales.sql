DROP TABLE IF EXISTS stage.customers;

CREATE TABLE stage.customers AS
SELECT
    c.id,
    c.name as name,
    c.age_int as age,
    c.country as country_2,
    c.country
FROM spectrum.customers c;


DROP TABLE IF EXISTS reporting.customers;

CREATE TABLE reporting.customers AS
SELECT
    c.id,
    c.name,
    c.age
FROM stage.customers c;

DROP TABLE IF EXISTS stage.customer_sales;

CREATE TABLE stage.customer_sales AS
SELECT
    s.customer_id,
    s.total_quantity_sold,
    s.total_value_sold,
    s.number_of_purchases
FROM spectrum.sales s;


DROP TABLE IF EXISTS reporting.customer_sales;

CREATE TABLE reporting.customer_sales AS
SELECT
    c.name,
    c.age,
    s.total_quantity_sold,
    s.total_value_sold,
    s.number_of_purchases
FROM stage.customers c
LEFT JOIN stage.customer_sales s ON s.customer_id = c.id;
