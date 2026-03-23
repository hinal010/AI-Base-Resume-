import sqlite3

# Connect to your database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Delete the table
cursor.execute("DROP TABLE IF EXISTS user_job_roles")  # Replace 'education' with your table name

# Commit changes and close connection
conn.commit()
conn.close()

print("Table deleted successfully!")