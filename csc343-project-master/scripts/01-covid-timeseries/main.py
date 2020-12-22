
import argparse
import glob
import os

from datetime import date

import pandas as pd
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, default="../../data/01-covid-timeseries")
parser.add_argument("--outfile", type=str, default="combined.csv")
args = parser.parse_args()

blacklist = [l.strip() for l in open("blacklist").readlines()]
replacement = { l.strip().split(':')[0]: l.strip().split(':')[1] for l in open("replacement").readlines() }

files = glob.glob(os.path.join(args.data, '*.csv'))
df_global = None

for f in tqdm(files, leave=False):
    month, day, year = tuple([int(x) for x in os.path.basename(f).split('.')[0].split('-')])
    df_raw = pd.read_csv(f)
    cols = list(df_raw.columns.values)

    # define header names to accomodate different CSV header formats
    key_region = 'Country_Region' if 'Country_Region' in cols else 'Country/Region'
    key_subregion = 'Province_State' if 'Province_State' in cols else 'Province/State'

    # blacklists and replacement
    df_raw = df_raw[~df_raw[key_region].isin(blacklist)]
    df_raw[key_region] = df_raw.apply(
        lambda row: replacement[row[key_region]] if row[key_region] in replacement else row[key_region], axis=1
    )

    # For newer reports, reports are more granular than region/subregion.
    # In these cases, we need to group the data by (region, subregion) and sum up the COVID numbers
    if 'Lat' in cols and 'Long_' in cols:
        grouped = df_raw.groupby([key_region, key_subregion], dropna=False).agg({
            'Lat': ['mean'],
            'Long_': ['mean'],
            'Confirmed': ['sum'],
            'Deaths': ['sum'],
            'Recovered': ['sum'],
        })
        grouped.columns = ['Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered']
        grouped = grouped.reset_index()

        df_raw = grouped
    else:
        grouped = df_raw.groupby([key_region, key_subregion], dropna=False).agg({
            'Confirmed': ['sum'],
            'Deaths': ['sum'],
            'Recovered': ['sum'],
        })
        grouped.columns = ['Confirmed', 'Deaths', 'Recovered']
        grouped = grouped.reset_index()

        df_raw = grouped

    # extract information from CSV
    data = {
        'reportdate': date(year, month, day),
        'region': df_raw[key_region].str.strip(),
        'subregion': df_raw.where(pd.notna(df_raw[key_subregion]), df_raw[key_region], axis=0)[key_subregion].str.strip(),
        'lat': df_raw['Lat'] if 'Lat' in cols else None,
        'lng': df_raw['Long_'] if 'Long_' in cols else None,
        'confirmed': df_raw['Confirmed'].fillna(0).astype('int32'),
        'deaths': df_raw['Deaths'].fillna(0).astype('int32'),
        'recovered': df_raw['Recovered'].fillna(0).astype('int32')
    }

    # append the content of this file
    df = pd.DataFrame.from_dict(data)
    if df_global is None: df_global = df
    else: df_global = df_global.append(df, ignore_index=True)

df_global.sort_values(by=['reportdate', 'region', 'subregion'], inplace=True)

df_global.to_csv(args.outfile, index=False)
