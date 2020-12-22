SET search_path to covid_project;

-- drop if exists

\Copy regions FROM ./04-regions.csv With CSV DELIMITER ',' HEADER;

\Copy covid_timeseries FROM ./01-covid-timeseries.csv With CSV DELIMITER ',' HEADER;
\Copy gdp FROM 02-gdp.csv With CSV DELIMITER ',' HEADER;
\Copy economic_indicators FROM ./03-economic-indicators.csv With CSV DELIMITER ',' HEADER;
\Copy development_index FROM ./05-development-index.csv With CSV DELIMITER ',' HEADER;
\Copy education_indicators FROM ./06-education-indicators.csv With CSV DELIMITER ',' HEADER;
