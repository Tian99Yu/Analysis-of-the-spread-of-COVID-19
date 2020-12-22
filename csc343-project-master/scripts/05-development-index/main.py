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

if __name__ == "__main__":
    # import the required data
    raw_hospital_per_1kcapita = pd.read_csv(
        "../../data/05-development-index/Hospital_per_capita/Hospital_per_1kcapita.csv")
    raw_primary_school_enrollment_rate = pd.read_csv(
        "../../data/05-development-index/primary_school_enrollment_rate/primary_school_enrollment_rate.csv")
    raw_secondary_school_enrollment_rate = pd.read_csv(
        "../../data/05-development-index/Secondary_school_enrollment_rate/Secondary_school_enrollment_rate.csv")
    raw_dev_index = pd.read_csv(
        "../../data/05-development-index/Human_development_index.csv")

    raw_hospital_per_1kcapita = filter_country(raw_hospital_per_1kcapita)
    raw_primary_school_enrollment_rate = filter_country(raw_primary_school_enrollment_rate)
    raw_secondary_school_enrollment_rate = filter_country(raw_secondary_school_enrollment_rate)
    raw_dev_index = filter_country(raw_dev_index)

    # data dict use to generate the final data, Dic[country_name, List[hospital, human, school]]
    data_hospital = {}

    # clean hospital data
    cur_df = raw_hospital_per_1kcapita
    # select the rows that are not NULL for year 2012 ~ 2015
    cur_df = cur_df.loc[(cur_df["2012"].notna()) | (cur_df["2013"].notna()) | (
        cur_df["2014"].notna()) | (cur_df["2015"].notna())]
    # select the latest row that is not NULL as the hospital per k capita we use in the DF

    for i, row in cur_df.iterrows():
        v_2012, v_2013, v_2014, v_2015 = row["2012"], row["2013"], row["2014"], \
                                         row["2015"]
        if pd.notna(v_2015):
            data_hospital[row["Country Name"]] = v_2015
        elif pd.notna(v_2014):
            data_hospital[row["Country Name"]] = v_2014
        elif pd.notna(v_2013):
            data_hospital[row["Country Name"]] = v_2013
        else:
            data_hospital[row["Country Name"]] = v_2012

    # clean and get the column for human development
    data_human = {}
    # get rid of the space between each columns
    cur_df = raw_dev_index[
        [c for c in raw_dev_index.columns if "Unnamed" not in c]]
    cur_df = cur_df.iloc[:-19, :]

    cur_df = cur_df.loc[(cur_df["2018"] != "..") | (cur_df["2017"] != "..") | (
            cur_df["2016"] != "..") | (cur_df["2015"] != "..")]

    for i, row in cur_df.iterrows():
        if row["2018"] != "..":
            data_human[row["Country"]] = row["2018"]
        elif row["2017"] != "..":
            data_human[row["Country"]] = row["2017"]
        elif row["2016"] != "..":
            data_human[row["Country"]] = row["2016"]
        elif row["2015"] != "..":
            data_human[row["Country"]] = row["2015"]

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

    # merge the three dicts
    p_s = set(data_primary_school.keys())
    s_s = set(data_secondary_school.keys())
    d_h_k = set(data_hospital.keys())
    d_h_d = set(data_human.keys())
    all_countries = p_s.union(s_s).union(d_h_k).union(d_h_d)


    def return_val(val, dic):
        return dic[val] if val in dic else np.nan

    final_result = []
    for country in all_countries:
        v1 = return_val(country, data_hospital)
        v2 = return_val(country, data_human)
        v3 = return_val(country, data_primary_school)
        v4 = return_val(country, data_secondary_school)
        final_result.append([country, v1, v2, v3, v4])

    result = pd.DataFrame(np.array(final_result),
                          columns=["region", "hospitals_per_1k",
                                   "human_development_index",
                                   "school_enrollment_primary",
                                   "school_enrollment_secondary"])

    result = result.astype(
        {"region": "string", "hospitals_per_1k": 'float32',
         "human_development_index": 'float32',
         "school_enrollment_primary": 'float32',
         "school_enrollment_secondary": 'float32'})



    result.to_csv("../../schema/05-development-index.csv", index=False)
