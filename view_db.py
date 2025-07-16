import sqlite3

conn = sqlite3.connect("tweets.db")
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("📦 Tables:", tables)

# Show contents of the displayed_tweets table
cursor.execute("SELECT * FROM displayed_tweets;")
rows = cursor.fetchall()

print("\n📄 Rows in displayed_tweets:")
for row in rows:
    print(row)

conn.close()
