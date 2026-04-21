import sqlite3 # Tool to connect to the database file

import sqlite3

connection = sqlite3.connect('database.db')

# We use DROP TABLE to ensure we start with a clean slate
connection.execute('DROP TABLE IF EXISTS resources') 

# This creates the table with all necessary columns
connection.execute('''
    CREATE TABLE resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        desc TEXT NOT NULL,
        lat REAL,
        lon REAL,
        phone TEXT
    )
''')

# Now the INSERT will work because the 'phone' column exists
connection.execute("INSERT INTO resources (title, category, desc, lat, lon, phone) VALUES (?, ?, ?, ?, ?, ?)",
            ('Springs Health Clinic', 'health', 'Located near the station.', -26.2500, 28.4333, '0115551234'))

connection.commit()
connection.close()
print("Database initialized successfully!")