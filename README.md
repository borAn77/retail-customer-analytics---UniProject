# Retail Customer Analytics – 604IT Big Data

Analysis of one year of online retail sales to find which products a UK-based gift retailer should advertise, and when.

## Dataset
- Source: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33 (downloaded from Kaggle)
- Licence: CC BY 4.0
- Size: 541,909 rows, 8 columns, December 2010 – December 2011
- Columns:
  - InvoiceNo – invoice number (starts with "C" if cancelled)
  - StockCode – product code
  - Description – product name
  - Quantity – units per line
  - InvoiceDate – date and time of the order
  - UnitPrice – price per unit (£)
  - CustomerID – customer number (missing for ~25% of rows)
  - Country – customer's country
- Included: `sample_online_retail.csv` (first 1,000 rows)
- The full file is not included because of its size. It is publicly available at the link above.
- `online_retail.csv` and `retail.db` are excluded from this repository via `.gitignore`.

## Requirements
- Python 3
- pandas, mlxtend


## How to run
Put `online_retail.csv` in the folder you run the commands from, then run the scripts in this order:

1. `python build_db.py` – loads the CSV into a staging table, cleans it (5 rules) and builds the SQLite database `retail.db`
2. `python test_constraints.py` – tries to insert invalid rows (negative quantity, missing order) and checks that the database rejects them
3. `python queries.py` – runs the SQL queries: top 10 products, monthly revenue, autumn (Sep–Nov) revenue share
4. `python mining.py` – finds products bought together with the Apriori algorithm (min_support = 0.02)

## Database
SQLite, 4 tables: `Customer`, `Invoice`, `InvoiceItem`, `Product`, with primary keys, foreign keys and CHECK constraints. See `ERD.png`.

## Results (after cleaning)
- 522,567 rows, 19,771 invoices, 4,333 customers, 3,803 products
- Revenue peaks in November 2011 (£1.45M)
- 198 association rules found

## Configuration
No big data framework configuration files are needed. The project uses SQLite and pandas.