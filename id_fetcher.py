# save_ids.py
import tweepy
import json
import os
from dotenv import load_dotenv

load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(BEARER_TOKEN)

with open('twitter_handle_names.json', 'r') as f:
    config = json.load(f)

handles = config['twitter_handles']
twitter_ids = {}

for handle in handles:
    try:
        user = client.get_user(username=handle)
        if user.data:
            twitter_ids[handle] = str(user.data.id)
            print(f"✅ {handle}: {user.data.id}")
    except Exception as e:
        print(f"❌ Failed to get ID for {handle}: {e}")

with open('twitter_ids.json', 'w') as f:
    json.dump(twitter_ids, f, indent=2)

print("\n🎉 All available Twitter IDs cached in twitter_ids.json")
