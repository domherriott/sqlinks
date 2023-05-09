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
