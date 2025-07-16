import sqlite3

DB_PATH = "tweet_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS displayed_tweets (
            tweet_id TEXT PRIMARY KEY,
            text TEXT,
            author TEXT,
            created_at TEXT,
            url TEXT,
            media TEXT, -- comma-separated list of media URLs
            shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def is_tweet_displayed(tweet_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM displayed_tweets WHERE tweet_id = ?", (tweet_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"❌ Error checking tweet in database: {e}")
        return False


def mark_tweet_as_displayed(tweet):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        media_str = ",".join(tweet.get("media", [])) if tweet.get("media") else ""

        cursor.execute("""
            INSERT OR IGNORE INTO displayed_tweets (
                tweet_id, text, author, created_at, url, media
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tweet['id'],
            tweet['text'],
            tweet['author'],
            tweet.get('created_at', ''),
            tweet['url'],
            media_str
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Error inserting tweet into database: {e}")
