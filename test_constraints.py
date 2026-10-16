import sqlite3

# 1. Connect to the SQLite database
con = sqlite3.connect('retail.db')

# 2. Enable Foreign Key constraints for the current connection
con.execute("PRAGMA foreign_keys = ON;")

cur = con.cursor()

# Fetch a valid InvoiceNo and StockCode to avoid Foreign Key errors during the CHECK constraint test
cur.execute("SELECT InvoiceNo FROM Invoice LIMIT 1;")
valid_invoice_no = cur.fetchone()[0]

cur.execute("SELECT StockCode FROM Product LIMIT 1;")
valid_stock_code = cur.fetchone()[0]

# 3. Test 1: Verify CHECK constraint (Insert a row with Quantity = -1)
print("--- Test 1: Testing CHECK Constraint ---")
try:
    cur.execute("""
        INSERT INTO InvoiceItem (InvoiceNo, StockCode, Quantity, UnitPrice)
        VALUES (?, ?, -1, 10.0);
    """, (valid_invoice_no, valid_stock_code))
    print("FAILED: CHECK constraint did not trigger!")
except sqlite3.IntegrityError as e:
    print(f"PASSED: CHECK constraint successfully triggered -> {e}")

# 4. Test 2: Verify Foreign Key constraint (Insert a row with a non-existent InvoiceNo)
print("\n--- Test 2: Testing Foreign Key Constraint ---")
try:
    invalid_invoice_no = "XXXXXX"
    cur.execute("""
        INSERT INTO InvoiceItem (InvoiceNo, StockCode, Quantity, UnitPrice)
        VALUES (?, ?, 1, 10.0);
    """, (invalid_invoice_no, valid_stock_code))
    print("FAILED: Foreign Key constraint did not trigger!")
except sqlite3.IntegrityError as e:
    print(f"PASSED: Foreign Key constraint successfully triggered -> {e}")

# 6. Roll back any uncommitted changes and close the database connection
con.rollback()
con.close()