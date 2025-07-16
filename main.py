import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from twitter_fetcher import fetch_tweets
from display import TweetDisplay
from database import init_db  # ✅ Import DB initializer


def main():
    app = QApplication(sys.argv)

    # ✅ Initialize database and tables (if not already created)
    init_db()

    # Fetch tweets (real + mock)
    tweets = fetch_tweets()
    if not tweets:
        print("⚠️ No tweets to display.")
        sys.exit(0)

    current_index = 0
    autoplay_timer = QTimer()
    window = None  # Forward declaration

    def show_next():
        nonlocal current_index
        try:
            current_index = (current_index + 1) % len(tweets)
            tweet = tweets[current_index]
            window.update_tweet(tweet)
            print(f"➡️ Showing tweet {current_index + 1}/{len(tweets)}: @{tweet['author']}")
        except Exception as e:
            print(f"❌ Failed to show next tweet: {e}")

    def show_prev():
        nonlocal current_index
        try:
            current_index = (current_index - 1) % len(tweets)
            tweet = tweets[current_index]
            window.update_tweet(tweet)
            print(f"⬅️ Showing tweet {current_index + 1}/{len(tweets)}: @{tweet['author']}")
        except Exception as e:
            print(f"❌ Failed to show previous tweet: {e}")

    def stop_autoplay():
        if autoplay_timer.isActive():
            autoplay_timer.stop()
            print("⏸ Autoplay stopped.")
        else:
            print("⚠️ Autoplay is already stopped.")

    def exit_app():
        print("👋 Exiting Tweet Viewer.")

    # Initialize the main window
    try:
        window = TweetDisplay(on_next=show_next, on_prev=show_prev, on_exit=exit_app)
        window.stop_autoplay = stop_autoplay  # Inject stop_autoplay method
        first_tweet = tweets[current_index]
        window.update_tweet(first_tweet)
        window.show()
        print(f"✅ Initial tweet loaded: @{first_tweet['author']}")
    except Exception as e:
        print(f"❌ Error initializing TweetDisplay: {e}")
        sys.exit(1)

    # Start autoplay (next tweet every 10 seconds)
    autoplay_timer.timeout.connect(show_next)
    autoplay_timer.start(10000)  # 10 seconds
    window.autoplay_timer = autoplay_timer  # Optional: used inside window if needed

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
