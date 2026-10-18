import pandas as pd
import sqlite3

# 1. Reading data and database connection
df = pd.read_csv('online_retail.csv', encoding='latin-1')

con = sqlite3.connect('retail.db')
con.execute("PRAGMA foreign_keys = ON")

df.to_sql('staging', con, if_exists='replace', index=False)

print("Staging row count:", pd.read_sql('SELECT COUNT(*) FROM staging', con).iloc[0, 0])

# 2. Data cleaning steps
df_no_dup = df.drop_duplicates()
df_clean = df_no_dup[~df_no_dup['InvoiceNo'].str.startswith('C')]
df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]
df_clean = df_clean[~df_clean['StockCode'].isin(['POST', 'DOT', 'M', 'C2', 'D', 'S', 'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'PADS', 'B'])].copy()

# Remove uncancelled original orders of massive cancelled transactions (Manual Outlier Removal)
cancelled_original_invoices = ['581483', '541431']
df_clean = df_clean[~df_clean['InvoiceNo'].isin(cancelled_original_invoices)]

df_clean['StockCode'] = df_clean['StockCode'].str.upper()

print("Cleaned df size:", df_clean.shape)
print("Unique StockCode count:", df_clean['StockCode'].nunique())

# 3. Dropping tables (In reverse order: child -> parent)
con.execute("DROP TABLE IF EXISTS InvoiceItem")
con.execute("DROP TABLE IF EXISTS Invoice")
con.execute("DROP TABLE IF EXISTS Product")
con.execute("DROP TABLE IF EXISTS Customer")

# 4. Creating tables
con.execute("""
CREATE TABLE Customer (
    CustomerID INTEGER PRIMARY KEY
)
""")

con.execute("""
CREATE TABLE Product (
    StockCode TEXT PRIMARY KEY,
    Description TEXT
)
""")

con.execute("""
CREATE TABLE Invoice (
    InvoiceNo TEXT PRIMARY KEY,
    InvoiceDate TEXT,
    Country TEXT,
    CustomerID INTEGER,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
)
""")

con.execute("""
CREATE TABLE InvoiceItem (
    InvoiceItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    InvoiceNo TEXT NOT NULL,
    StockCode TEXT NOT NULL,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    UnitPrice REAL NOT NULL CHECK (UnitPrice > 0),
    FOREIGN KEY (InvoiceNo) REFERENCES Invoice(InvoiceNo),
    FOREIGN KEY (StockCode) REFERENCES Product(StockCode)
)
""")

con.commit()

# --- 1. POPULATING CUSTOMER TABLE ---
customer_df = (
    df_clean['CustomerID']
    .dropna()
    .drop_duplicates()
    .astype(int)
    .to_frame(name='CustomerID')
)
customer_df.to_sql('Customer', con, if_exists='append', index=False)

# --- 2. POPULATING PRODUCT TABLE ---
def get_most_frequent_desc(series):
    modes = series.dropna().mode()
    return modes.iloc[0] if not modes.empty else None

product_df = (
    df_clean
    .groupby('StockCode')['Description']
    .agg(get_most_frequent_desc)
    .reset_index()
)
product_df.to_sql('Product', con, if_exists='append', index=False)

# --- 3. POPULATING INVOICE TABLE ---

df_clean_inv = df_clean.copy()

# Fix: format parameter removed, Pandas automatically detects ISO format
df_clean_inv['InvoiceDate_dt'] = pd.to_datetime(df_clean_inv['InvoiceDate'])

invoice_df = (
    df_clean_inv
    .groupby('InvoiceNo')
    .agg(
        InvoiceDate=('InvoiceDate_dt', 'min'),
        Country=('Country', 'first'),
        CustomerID=('CustomerID', 'first')
    )
    .reset_index()
)

# Converting datetime values to standard string format ('YYYY-MM-DD HH:MM:SS') for SQLite
invoice_df['InvoiceDate'] = invoice_df['InvoiceDate'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Using nullable 'Int64' for CustomerID
invoice_df['CustomerID'] = invoice_df['CustomerID'].astype('Int64')

# Writing prepared data into the 'Invoice' table
invoice_df.to_sql('Invoice', con, if_exists='append', index=False)

# --- INVOICE TABLE CHECK AND VALIDATION ---
db_invoice_count = pd.read_sql('SELECT COUNT(*) FROM Invoice', con).iloc[0, 0]
clean_unique_invoices = df_clean['InvoiceNo'].nunique()

print(f"\nRow count in Invoice table: {db_invoice_count}")
print(f"Unique InvoiceNo count in df_clean: {clean_unique_invoices}")

if db_invoice_count == clean_unique_invoices:
    print("SUCCESS: Invoice table populated successfully and row counts match exactly!")
else:
    print("WARNING: Row counts do not match!")

# --- 4. POPULATING INVOICEITEM TABLE ---

# 1. Select the required 4 columns from df_clean
invoice_item_df = df_clean[['InvoiceNo', 'StockCode', 'Quantity', 'UnitPrice']]

# 2. Insert data into 'InvoiceItem' table (InvoiceItemID will be automatically assigned via AUTOINCREMENT)
invoice_item_df.to_sql('InvoiceItem', con, if_exists='append', index=False)

# --- INVOICEITEM TABLE CHECK AND VALIDATION ---
db_item_count = pd.read_sql('SELECT COUNT(*) FROM InvoiceItem', con).iloc[0, 0]
expected_item_count = len(df_clean)

print(f"\nRow count in InvoiceItem table: {db_item_count}")
print(f"Expected row count (df_clean.shape[0]): {expected_item_count}")

if db_item_count == expected_item_count:
    print("SUCCESS: InvoiceItem table populated successfully and row counts match exactly!")
else:
    print("WARNING: Row counts do not match!")

con.close()