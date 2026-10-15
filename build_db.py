import pandas as pd
import sqlite3

df = pd.read_csv('online_retail.csv', encoding='latin-1')

con = sqlite3.connect('retail.db') 

df.to_sql('staging', con, if_exists='replace', index=False)

print(pd.read_sql('SELECT COUNT(*) FROM staging', con))

df_no_dup = df.drop_duplicates()
df_clean = df_no_dup[~df_no_dup['InvoiceNo'].str.startswith('C')]
df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]
df_clean = df_clean[~df_clean['StockCode'].isin(['POST', 'DOT', 'M', 'C2', 'D', 'S', 'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'PADS', 'B'])].copy()
df_clean['StockCode'] = df_clean['StockCode'].str.upper()

print(df_clean.shape)
print(df_clean['StockCode'].nunique())
