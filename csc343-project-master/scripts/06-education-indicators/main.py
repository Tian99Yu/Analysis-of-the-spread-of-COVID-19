import pandas as pd
import numpy as np

# blacklisting and replacement
blacklist = [l.strip() for l in open("blacklist").readlines()]
replacement = { l.strip().split(':')[0]: l.strip().split(':')[1] for l in open("replacement").readlines() }

def get_rid_of_na(df, col_start, col_finish):
    """
    return a df. The rows of that df has at least one not NULL value in col_start to col_finish
    :param df:
    :param col_start:
    :param col_finish:
    :return:
    """
    # get rid of the rows that are all NULL
    acc = np.array([False] * df.shape[0])
    for i in range(col_start, col_finish):
        acc = acc | df.iloc[:, i].notna()
    df = df.loc[acc]
    new_col = []
    # get the left most col value that is not NULL from col_start to col_finish
    for i, row in df.iterrows():
        start = col_finish
        found = False
        tmp = None
        while not found:
            tmp = row[start]
            if pd.notna(tmp):
                found = True
                break
            start -= 1

        new_col.append(tmp)
    # append it to a new col and return
    df.insert(len(df.columns), "new_col", new_col)
    return df

def filter_country(df):
    cols = list(df.columns.values)
    key_region = 'Country Name' if 'Country Name' in cols else 'Country'

    # strip region names
    df[key_region] = df[key_region].str.strip()

    # do replacement and blacklisting
    df = df[~df[key_region].isin(blacklist)]
    df[key_region] = df.apply(
        lambda row: replacement[row[key_region]] if row[key_region] in replacement else row[key_region], axis=1
    )

    return df

# import all the datas
raw_primary_school_enrollment_rate = pd.read_csv(
    "../../data/05-development-index/primary_school_enrollment_rate/primary_school_enrollment_rate.csv")
raw_secondary_school_enrollment_rate = pd.read_csv(
    "../../data/05-development-index/Secondary_school_enrollment_rate/Secondary_school_enrollment_rate.csv")
raw_literacy_rate = pd.read_csv(
    "../../data/06-education-indicators/literacy_rate/literacy_rate_of_people_15_above.csv")
raw_r_and_d_exp = pd.read_csv(
    "../../data/06-education-indicators/r_and_d_exp/r_and_d_expenditure.csv")

raw_primary_school_enrollment_rate = filter_country(raw_primary_school_enrollment_rate)
raw_secondary_school_enrollment_rate = filter_country(raw_secondary_school_enrollment_rate)
raw_literacy_rate = filter_country(raw_literacy_rate)
raw_r_and_d_exp = filter_country(raw_r_and_d_exp)

# clean and get the dict for literacy_rate
data_lit = {}
cur_df = raw_literacy_rate
cur_df = get_rid_of_na(cur_df, 60, 65)
for i, row in cur_df.iterrows():
    data_lit[row["Country Name"]] = row["new_col"]

# clean and get the dict for r&d
data_r_and_d = {}
cur_df = raw_r_and_d_exp
cur_df = get_rid_of_na(cur_df, 60, 65)
for i, row in cur_df.iterrows():
    data_r_and_d[row["Country Name"]] = row["new_col"]

# clean and get the data for primary school
data_primary_school = {}
cur_df = raw_primary_school_enrollment_rate
cur_df = get_rid_of_na(cur_df, 60, 65)
for i, row in cur_df.iterrows():
    data_primary_school[row["Country Name"]] = row["new_col"]

# clean and get the data for secondary school
data_secondary_school = {}
cur_df = raw_secondary_school_enrollment_rate
cur_df = get_rid_of_na(cur_df, 60, 65)
for i, row in cur_df.iterrows():
    data_secondary_school[row["Country Name"]] = row["new_col"]

# merge the dictionaries together
k_lit = set(data_lit.keys())
k_rnd = set(data_r_and_d.keys())
k_p_s = set(data_primary_school.keys())
k_s_s = set(data_secondary_school.keys())
all_countries = k_lit.union(k_rnd).union(k_p_s).union(k_s_s)

final_result = []


def return_val(val, dic):
    return dic[val] if val in dic else np.nan


for country in all_countries:
    v1 = return_val(country, data_lit)
    v2 = return_val(country, data_r_and_d)
    v3 = return_val(country, data_primary_school)
    v4 = return_val(country, data_secondary_school)
    final_result.append([country, v1, v2, v3, v4])

result = pd.DataFrame(np.array(final_result), columns=["region",
                                                       "literacy_rate",
                                                       "rnd_expenditure",
                                                       "perc_school_enrollment_primary",
                                                       "perc_school_enrollment_secondary"]).astype(
    {"region": 'string',
     "literacy_rate": 'float32',
     "rnd_expenditure": 'float32',
     "perc_school_enrollment_primary": 'float32',
     "perc_school_enrollment_secondary": 'float32'})
result.to_csv("../../schema/06-education-indicators.csv", index=False)
