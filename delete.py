import sqlite3

# Connect to your database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Delete the table
cursor.execute("DROP TABLE IF EXISTS educations")  # Replace 'education' with your table name

# Commit changes and close connection
conn.commit()
conn.close()

print("Table deleted successfully!")