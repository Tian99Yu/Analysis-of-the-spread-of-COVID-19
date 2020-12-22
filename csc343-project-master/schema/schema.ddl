drop schema if exists covid_project cascade;
create schema covid_project;
set search_path to covid_project;

create table regions
(
	region varchar(64) not null primary key,
	population int not null,
	habitable_area real
);

create table covid_timeseries
(
	reportdate date not null,
	region varchar(64) references regions(region),
	subregion varchar(64) not null,
	lat real,
	lng real,
	confirmed int constraint confirmed_not_negative check (confirmed >= 0),
	death int constraint death_not_negative check (death >= 0),
	recovered int constraint recovered_not_negative check (recovered >= 0),
	primary key (reportdate, region, subregion)
);

create table gdp
(
    region varchar(64) references regions(region),
    year int not null,
    quarter int not null constraint valid_quarter check (quarter >= 1 and quarter <= 4),
    gdp real not null,
    primary key (region, year, quarter)
);

create table economic_indicators
(
    region varchar(64) references regions(region),
    year int not null,
    household_savings real,
    gdp real,
    household_debt real,
    primary key (region, year)
);

create table development_index
(
    region varchar(64) primary key references regions(region),
    hospitals_per_1k real,
    human_capital_index real,
    school_enrollment_primary real,
    school_enrollment_secondary real
);

create table education_indicators
(
    region varchar(64) primary key references regions(region),
    perc_school_enrollment_primary real,
    perc_school_enrollment_secondary real,
    literacy_rate real,
    rnd_expenditure real
);
