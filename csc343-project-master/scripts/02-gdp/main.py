
import argparse
import glob
import os

from datetime import date

import pandas as pd
from forex_python.converter import CurrencyRates
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, default="../../data/02-gdp/QNA_04112020161339631.csv")
parser.add_argument("--outfile", type=str, default="combined.csv")
args = parser.parse_args()

blacklist = [l.strip() for l in open("blacklist").readlines()]
replacement = { l.strip().split(':')[0]: l.strip().split(':')[1] for l in open("replacement").readlines() }

df = pd.read_csv(args.data)

# CQRSA: National currency, current prices, quarterly levels, seasonally adjusted
# df = df[df['MEASURE'] == 'CQRSA']

# CQR: National currency, current prices, quarterly levels	
df = df[df['MEASURE'] == 'CQR']

# B1_GE: Gross domestic product - expenditure approach
df = df[df['SUBJECT'] == 'B1_GE']

df_rates = pd.read_csv('exchange.csv')
codes = list(df_rates['Code'])
rates = list(df_rates['USDPerUnit'])

exch = dict()
for c, r in zip(codes, rates): exch[c] = r

data = {
    'region': df['Country'],
    'year': df['Period'].str.slice(start=3),
    'quarter': df['Period'].str.slice(start=1, stop=2),
    'gdp': df.apply(lambda row: row['Value'] * exch[row['Unit Code']], axis=1)
}

df_final = pd.DataFrame.from_dict(data)
df_final = df_final[~df_final['region'].isin(blacklist)]
df_final['region'] = df_final.apply(
    lambda row: replacement[row['region']] if row['region'] in replacement else row['region'], axis=1
)

df_final.to_csv(args.outfile, index=False)


