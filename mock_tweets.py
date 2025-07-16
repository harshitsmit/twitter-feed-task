import random
from datetime import datetime, timedelta

def generate_mock_tweet(include_image=False, force_author=None):
    fake_authors = ["OpenAI", "TechInsider", "PythonHub", "CodeMaster", "AI_Updates"]
    sample_texts = [
        "Exciting updates coming to our platform next week. Stay tuned!",
        "Did you know Python 3.12 is now even faster? 🚀",
        "5 tips to write cleaner, more efficient code.",
        "Our AI model just broke another benchmark. 🤖",
        "Here's a quick breakdown of LLM architecture in 2024.",
        "Mock tweets are great for testing real-time apps!",
        "Try coding without caffeine... just kidding. ☕",
    ]

    author = force_author if force_author else random.choice(fake_authors)
    text = random.choice(sample_texts)

    created_at = datetime.now() - timedelta(hours=random.randint(0, 24), minutes=random.randint(0, 59))
    created_at_str = created_at.strftime("%b %d, %Y %I:%M %p")

    tweet_url = f"https://x.com/{author}/status/{random.randint(1000000000, 9999999999)}"

    # Media list (can contain 0–2 items)
    media = []
    if include_image:
        for _ in range(random.randint(1, 2)):  # up to 2 images
            media.append(f"https://picsum.photos/seed/{random.randint(1000, 9999)}/800/400")

    return {
        "id": f"mock-{random.randint(1000, 9999)}",
        "text": text,
        "author": author,
        "created_at": created_at_str,
        "url": tweet_url,
        "media": media,
        "mock": True
    }

def generate_mock_tweets(n=10, force_author=None):
    tweets = []
    media_indices = random.sample(range(n), k=min(2, n))  # 1–2 mock tweets with media

    for i in range(n):
        tweets.append(generate_mock_tweet(
            include_image=(i in media_indices),
            force_author=force_author
        ))

    return tweets
