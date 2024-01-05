DROP TABLE IF EXISTS stage.applications;

CREATE TABLE stage.applications AS
WITH clean_raw_table AS (
    SELECT
    s.id
    , s.dateplaced :: TIMESTAMP as dateplaced
    , s.sellerfulfillmentorderid
    , s.quantity
    , sku
    , s.tenant
    , f_clean_postcode(s.postcode) as postcode
    , s.towncity
    , s.countrycode
    , s.subjectid
    , CASE
        WHEN s.orderstatus LIKE '202%' THEN NULL
        ELSE s.orderstatus
      END AS orderstatus
    , "$path" as filename
    ,to_date(regexp_substr("$path",  '[0-9]{4}-[0-9]{2}-[0-9]{2}'), 'YYYY-MM-DD')  as file_date
FROM
    raw.stage_logistics_applications s
WHERE id LIKE '%-%'
), dedupe as (
    SELECT id,
           dateplaced,
           sellerfulfillmentorderid,
           quantity,
           sku,
           kit_type,
           tenant,
           postcode,
           towncity,
           countrycode,
           subjectid,
           orderstatus,
           filename,
           file_date,
           row_number() over (partition by sellerfulfillmentorderid order by  sellerfulfillmentorderid, file_date desc) RN
    FROM clean_raw_table
)
SELECT id,
       dateplaced,
       sellerfulfillmentorderid,
       quantity,
       sku,
       kit_type,
       tenant,
       postcode,
       towncity,
       countrycode,
       subjectid,
       orderstatus
FROM dedupe
WHERE  rn = 1;

DROP TABLE IF EXISTS reporting.applications;

CREATE TABLE reporting.applications AS
SELECT
    a.id
    , CONVERT_TIMEZONE('UTC', 'Europe/London', a.dateplaced) dateplaced
    , a.sellerfulfillmentorderid
    , a.quantity
    , a.sku
    , a.kit_type
    , a.tenant
    , a.postcode
    , a.towncity
    , a.countrycode
    , a.subjectid
    , a.orderstatus
    , rp.postcode_district AS postal_district
    , rp.postcode_area_derived AS postal_area
    , o.district
    , rp.local_authority_district_name as local_authority
    , rp.region_name as region
    , rp.country_name as country
    , rpavg.longitude
    , rpavg.latitude
FROM
    stage.applications a
 	LEFT JOIN stage.os_geographical_data AS o ON a.postcode = o.postcode
	LEFT JOIN reporting.reference_postcode AS rp ON a.postcode = rp.postcode
	LEFT JOIN reporting.reference_postal_district_averaged_long_lat rpavg ON f_trim_postcode(f_clean_postcode(a.postcode)) = rpavg.postal_district;


DROP TABLE IF EXISTS reporting.capacity_actuals;

CREATE TABLE reporting.capacity_actuals(
	value_type					varchar NULL,
	processing_date				date NULL,
	actuals_value				numeric(5,2)  NULL);

INSERT INTO reporting.apacity_actuals(
SELECT
	lab AS lab,
	"value type" AS value_type,
	to_date("date", 'DD/MM/YYYY') AS processing_date,
	"actuals value" :: numeric(5,2) AS actuals_value
FROM
    raw.capacity_actuals);

DROP TABLE IF EXISTS reporting.capacity_forecast;

CREATE TABLE reporting.capacity_forecast(
	value_type					varchar NULL,
	forecast_date				date NULL,
	processing_date				date NULL,
	plan_value					numeric(5,2) NULL);

INSERT INTO reporting.labs_capacity_forecast(
SELECT
	"value type" AS value_type,
	to_date("forecast date", 'DD/MM/YYYY') AS forecast_date,
	to_date("date", 'DD/MM/YYYY') AS processing_date,
	"plan value" :: numeric(5,2) AS plan_value
FROM
    raw.labs_capacity_forecast);
