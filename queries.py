import sqlite3
import pandas as pd

# 1. Connect to the SQLite database
con = sqlite3.connect('retail.db')

# --- Query 1: Top 10 Products by Revenue ---
query_top_products = """
SELECT 
    p.StockCode,
    p.Description,
    SUM(i.Quantity * i.UnitPrice) AS Revenue
FROM InvoiceItem i
JOIN Product p ON i.StockCode = p.StockCode
GROUP BY p.StockCode, p.Description
ORDER BY Revenue DESC
LIMIT 10;
"""

df_top_products = pd.read_sql(query_top_products, con)
print("--- Top 10 Products by Revenue ---")
print(df_top_products)

# --- Query 2: Monthly Revenue ---
query_monthly_revenue = """
SELECT 
    strftime('%Y-%m', inv.InvoiceDate) AS Month,
    SUM(i.Quantity * i.UnitPrice) AS Revenue
FROM InvoiceItem i
JOIN Invoice inv ON i.InvoiceNo = inv.InvoiceNo
GROUP BY Month
ORDER BY Month ASC;
"""

df_monthly_revenue = pd.read_sql(query_monthly_revenue, con)
print("\n--- Monthly Revenue ---")
print(df_monthly_revenue)

# --- Query 3: Top 10 Products by Revenue in Autumn Peak (Sep - Nov 2011) ---
query_autumn_top_products = """
SELECT 
    p.StockCode,
    p.Description,
    SUM(i.Quantity * i.UnitPrice) AS Revenue
FROM InvoiceItem i
JOIN Product p ON i.StockCode = p.StockCode
JOIN Invoice inv ON i.InvoiceNo = inv.InvoiceNo
WHERE inv.InvoiceDate BETWEEN '2011-09-01' AND '2011-11-30 23:59:59'
GROUP BY p.StockCode, p.Description
ORDER BY Revenue DESC
LIMIT 10;
"""

df_autumn_top_products = pd.read_sql(query_autumn_top_products, con)
print("\n--- Top 10 Products by Revenue (Autumn Peak: Sep - Nov 2011) ---")
print(df_autumn_top_products)

# Close the database connection
con.close()