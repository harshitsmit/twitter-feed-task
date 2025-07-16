import tweepy
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from database import is_tweet_displayed, mark_tweet_as_displayed  # ✅ Add both
from mock_tweets import generate_mock_tweets
import time

# Load environment variables
load_dotenv()

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    raise ValueError("❌ BEARER_TOKEN not found in environment variables")

client = tweepy.Client(BEARER_TOKEN)


def get_twitter_handles():
    """Reads Twitter handles from twitter_handle_names.json"""
    try:
        with open('twitter_handle_names.json', 'r') as f:
            config = json.load(f)
            return config.get('twitter_handles', [])
    except Exception as e:
        print(f"❌ Failed to load twitter_handle_names.json: {e}")
        return []


def get_twitter_ids():
    """Loads cached Twitter user IDs from twitter_ids.json"""
    try:
        with open('twitter_ids.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ twitter_ids.json not found. Using only mock tweets.")
        return {}
    except Exception as e:
        print(f"❌ Error reading twitter_ids.json: {e}")
        return {}

def fetch_tweets():
    """Fetches tweets with media support, stores them, and falls back to mocks if API fails."""
    id_map = get_twitter_ids()
    all_tweets = []
    real_tweet_found = False

    try:
        for handle, user_id in id_map.items():
            try:
                response = client.get_users_tweets(
                    id=user_id,
                    max_results=5,
                    tweet_fields=["created_at", "text", "attachments"],
                    expansions=["attachments.media_keys"],
                    media_fields=["url", "preview_image_url", "type"]
                )
            except tweepy.TooManyRequests as rate_ex:
                reset_timestamp = getattr(rate_ex.response.headers, 'x-rate-limit-reset', None)
                if reset_timestamp:
                    reset_time = int(reset_timestamp) - int(time.time())
                    print(f"🚨 Rate limit hit. Try again in {reset_time} seconds.")
                else:
                    print("🚨 Rate limit hit. No reset time available.")
                raise  # Re-raise to trigger fallback to mock tweets

            media_map = {}
            if response.includes and "media" in response.includes:
                for media in response.includes["media"]:
                    media_map[media.media_key] = media

            if response.data:
                for tweet in response.data:
                    if not is_tweet_displayed(str(tweet.id)):
                        tweet_url = f"https://x.com/{handle}/status/{tweet.id}"

                        media_urls = []
                        if hasattr(tweet, "attachments") and "media_keys" in tweet.attachments:
                            for key in tweet.attachments["media_keys"]:
                                media_obj = media_map.get(key)
                                if media_obj:
                                    if media_obj.type == "photo":
                                        media_urls.append(media_obj.url)
                                    elif media_obj.type in ("video", "animated_gif"):
                                        media_urls.append(media_obj.preview_image_url)

                        tweet_data = {
                            "id": str(tweet.id),
                            "text": tweet.text,
                            "author": handle,
                            "created_at": tweet.created_at.strftime("%b %d, %Y %I:%M %p"),
                            "url": tweet_url,
                            "mock": False,
                            "media": media_urls
                        }

                        all_tweets.append(tweet_data)
                        mark_tweet_as_displayed(tweet_data)
                        real_tweet_found = True
                        break

            if real_tweet_found:
                break

    except tweepy.TooManyRequests:
        print("🚨 Falling back to mock tweets due to rate limiting.")
    except Exception as e:
        print(f"❌ Error fetching tweets: {e}")

    # Add mock tweets
    mock_count = 5 if real_tweet_found else 6
    mock_tweets = generate_mock_tweets(n=mock_count)
    all_tweets.extend(mock_tweets)

    return all_tweets
