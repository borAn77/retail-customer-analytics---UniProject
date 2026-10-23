import sqlite3
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Target sqlite database file containing the retail transactions
conn = sqlite3.connect("retail.db")
query = "SELECT InvoiceNo, StockCode FROM InvoiceItem"
df = pd.read_sql_query(query, conn)
conn.close()

# Pivot transactions into a binary basket matrix (invoices x products)
# Note: Generates ~19.7k x 3.8k matrix, takes 1-2 minutes to compute
basket = pd.crosstab(df["InvoiceNo"], df["StockCode"]) > 0

# Extract frequent product sets present in at least 2% of baskets
frequent_itemsets = apriori(basket, min_support=0.02, use_colnames=True)

# Generate rule metrics; passing num_itemsets to prevent positional arg errors in newer mlxtend versions
rules = association_rules(
    frequent_itemsets,
    metric="lift",
    min_threshold=1,
    num_itemsets=len(basket)
)

# Rank the generated associations based on lift metric
sorted_rules = rules.sort_values(by="lift", ascending=False)

# Display top 10 item associations
print(sorted_rules.head(10))