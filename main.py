import pandas as pd 

#Loading the dataset to our environment 
df = pd.read_csv('online_retail.csv', encoding='latin-1')

#print(df.shape)
#df.info()
#print(df.head())

print(df.duplicated().sum())

#print(df[df.duplicated()].head(10))

#print(df[(df['InvoiceNo'] == '536409') & (df['StockCode'] == '21866')])

df_no_dup  = df.drop_duplicates()
print(df_no_dup.shape)

df_clean = df_no_dup[~df_no_dup['InvoiceNo'].str.startswith('C')]

#print(df_clean.shape)

df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]

print(df_clean.shape)

print(df_clean['CustomerID'].isna().sum())

df_clean = df_clean[~df_clean['StockCode'].isin(['POST', 'DOT', 'M', 'C2', 'D','S', 'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'PADS', 'B'])]

print(df_clean.shape)

df_clean.to_csv('retail_clean.csv', index=False)