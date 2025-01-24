import json
import sqlite3
import os

conn = sqlite3.connect('database.db')

members_json = os.path.join(os.path.dirname(__file__), 'members.json')

with open(members_json) as f:
    members = json.load(f)
    usernames = members['usernames']
    for username in usernames:
        conn.execute(
            'INSERT OR IGNORE INTO users (username) VALUES (?)',
            (username,)
        )
        conn.execute(
            'UPDATE users SET is_member = 1 WHERE username = ?',
            (username,)
        )

conn.commit()
conn.close()
