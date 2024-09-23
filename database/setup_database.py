import sqlite3

# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect('listings.db')

cursor = conn.cursor()

# Listings Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    posted TEXT NOT NULL,
    price TEXT NOT NULL,
    link TEXT NOT NULL,
    description TEXT
)
''')

# Subscribers Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE
)
''')

# Commit changes and close
conn.commit()
conn.close()

print("Database and tables created successfully.")