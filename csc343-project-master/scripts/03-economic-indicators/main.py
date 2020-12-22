
import argparse
import glob
import sys
import os

from datetime import date
from functools import reduce

import pandas as pd
from forex_python.converter import CurrencyRates
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, default="../../data/03-economic-indicators/")
parser.add_argument("--outfile", type=str, default="combined.csv")
args = parser.parse_args()

blacklist = [l.strip() for l in open("blacklist").readlines()]
replacement = { l.strip().split(':')[0]: l.strip().split(':')[1] for l in open("replacement").readlines() }

df_savings = pd.read_csv(os.path.join(args.data, 'DP_LIVE_04112020173102616.csv'))
df_debt = pd.read_csv(os.path.join(args.data, 'DP_LIVE_04112020174821257.csv'))
df_gdp = pd.read_csv(os.path.join(args.data, 'DP_LIVE_04112020174733429.csv'))

# merge data into a single dataframe
df_savings = df_savings.rename(columns={'Value': 'household_savings'})[['LOCATION', 'TIME', 'household_savings']]
df_debt = df_debt.rename(columns={'Value': 'household_debt'})[['LOCATION', 'TIME', 'household_debt']]
df_gdp = df_gdp.rename(columns={'Value': 'gdp'})[['LOCATION', 'TIME', 'gdp']]

df_final = reduce(lambda l, r: pd.merge(l, r, on=['LOCATION', 'TIME'], how='outer'), [df_savings, df_debt, df_gdp])

# convert ISO country codes to full country names
isocountry = pd.read_csv("isocountry.csv")
cname, ccode = list(isocountry['Country']), [x.replace('\"', '').strip() for x in list(isocountry['Alpha-3 code'])]
cdict = { x:y for x, y in zip(ccode, cname) }

df_final = df_final[df_final['LOCATION'].isin(ccode)]
df_final['region'] = df_final.apply(lambda row: cdict[row['LOCATION']], axis=1)
df_final = df_final.rename(columns={'TIME': 'year'})[['region', 'year', 'household_savings', 'gdp', 'household_debt']]

df_final = df_final[~df_final['region'].isin(blacklist)]
df_final['region'] = df_final.apply(
    lambda row: replacement[row['region']] if row['region'] in replacement else row['region'], axis=1
)

df_final.to_csv(args.outfile, index=False)

