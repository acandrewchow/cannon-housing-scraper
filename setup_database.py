import sqlite3

# Connect to the SQLite database 
conn = sqlite3.connect('listings.db')

cursor = conn.cursor()

# Listings Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    posted TEXT NOT NULL,
    price TEXT NOT NULL,
    link TEXT NOT NULL UNIQUE,
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

conn.commit()
conn.close()

print("Database and tables created successfully.")