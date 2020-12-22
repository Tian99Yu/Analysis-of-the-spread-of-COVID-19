
import argparse
import glob
import os

from datetime import date

import pandas as pd
from forex_python.converter import CurrencyRates
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, default="../../data/04-regions/")
parser.add_argument("--outfile", type=str, default="combined.csv")
args = parser.parse_args()

df_popl = pd.read_csv(os.path.join(args.data, 'API_SP.POP.TOTL_DS2_en_csv_v2_1593924.csv'), skiprows=4)
df_land = pd.read_csv(os.path.join(args.data, 'API_AG.LND.TOTL.K2_DS2_en_csv_v2_1567646.csv'), skiprows=4)

df_popl = df_popl.rename(columns={'Country Name': 'region', '2019': 'population'})[['region', 'population']]
df_land = df_land.rename(columns={'Country Name': 'region', '2017': 'habitable_area'})[['region', 'habitable_area']]

# na's
print(df_popl['population'].isna().sum())
print(df_land['habitable_area'].isna().sum())
df_popl.dropna(inplace=True)
df_land.dropna(inplace=True)

df = df_popl.join(df_land, rsuffix='r')[['region', 'population', 'habitable_area']]
df['population'] = df['population'].astype('int32')
df.to_csv(args.outfile, index=False)
