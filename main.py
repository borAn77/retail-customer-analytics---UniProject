import pandas as pd 

# Load the dataset into the Pandas DataFrame using 'latin-1' encoding
df = pd.read_csv('online_retail.csv', encoding='latin-1')

# Optional dataset inspection step (currently commented out)
# print(df.shape)
# df.info()
# print(df.head())

# Count and display the total number of duplicate rows in the dataset
print(df.duplicated().sum())

# Inspect the first 10 duplicate rows (currently commented out)
# print(df[df.duplicated()].head(10))

# Inspect specific records based on InvoiceNo and StockCode (currently commented out)
# print(df[(df['InvoiceNo'] == '536409') & (df['StockCode'] == '21866')])

# Remove exact duplicate rows from the DataFrame
df_no_dup = df.drop_duplicates()
print(df_no_dup.shape)

# Filter out cancelled transactions (invoices starting with 'C')
df_clean = df_no_dup[~df_no_dup['InvoiceNo'].str.startswith('C')]

# Check dataset dimensions after removing cancelled orders (currently commented out)
# print(df_clean.shape)

# Keep only records with positive values for both Quantity and UnitPrice
df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]

print(df_clean.shape)

# Count and print the total number of missing CustomerID values
print(df_clean['CustomerID'].isna().sum())

# Exclude non-product system codes (postage, manual fees, bank charges, etc.)
df_clean = df_clean[~df_clean['StockCode'].isin(['POST', 'DOT', 'M', 'C2', 'D', 'S', 'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'PADS', 'B'])]

print(df_clean.shape)

# Export the cleaned dataset to a new CSV file without the row index
df_clean.to_csv('retail_clean.csv', index=False)