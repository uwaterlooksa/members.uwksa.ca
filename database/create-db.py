import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('DROP TABLE IF EXISTS users;')

conn.execute('''
CREATE TABLE users (
    USERNAME TEXT PRIMARY KEY,
    GIVEN_NAME TEXT,
    FAMILY_NAME TEXT,
    IS_MEMBER BOOLEAN DEFAULT FALSE
) WITHOUT ROWID;
''')

conn.commit()
conn.close()
