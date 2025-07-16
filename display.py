from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea
)
from PyQt5.QtGui import QPixmap, QFont, QImage
from PyQt5.QtCore import Qt
from screeninfo import get_monitors
import qrcode
import os
from urllib.request import urlopen

ASSETS_DIR = "assets"

def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_path = os.path.join(ASSETS_DIR, "temp_qr.png")
    img.save(img_path)
    return img_path

class TweetDisplay(QMainWindow):
    def __init__(self, on_next=None, on_prev=None, on_exit=None):
        super().__init__()

        self.on_next = on_next
        self.on_prev = on_prev
        self.on_exit = on_exit
        self.autoplay_timer = None

        monitor = get_monitors()[1] if len(get_monitors()) > 1 else get_monitors()[0]
        self.setGeometry(monitor.x, monitor.y, monitor.width, monitor.height)
        self.setWindowTitle("Twitter Feed")
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #000000; color: white;")

        # Fonts
        self.font_tweet = QFont("Segoe UI", 20)
        self.font_author = QFont("Segoe UI", 16, QFont.Bold)
        self.font_time = QFont("Segoe UI", 13)
        self.font_mock = QFont("Segoe UI", 12, QFont.StyleItalic)
        self.font_button = QFont("Segoe UI", 12)

        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(16)

        # Logo
        self.logo_label = QLabel()
        logo_path = os.path.join(ASSETS_DIR, "twitter_logo.png")
        self.logo_label.setPixmap(QPixmap(logo_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.main_layout.addWidget(self.logo_label, alignment=Qt.AlignLeft)

        # Tweet content
        self.tweet_label = QLabel()
        self.tweet_label.setFont(self.font_tweet)
        self.tweet_label.setWordWrap(True)
        self.main_layout.addWidget(self.tweet_label)

        self.author_label = QLabel()
        self.author_label.setFont(self.font_author)
        self.author_label.setStyleSheet("color: #1DA1F2;")
        self.main_layout.addWidget(self.author_label)

        self.time_label = QLabel()
        self.time_label.setFont(self.font_time)
        self.time_label.setStyleSheet("color: #8899A6;")
        self.main_layout.addWidget(self.time_label)

        self.qr_label = QLabel()
        self.qr_label.setFixedSize(160, 160)
        self.main_layout.addWidget(self.qr_label)

        self.mock_label = QLabel()
        self.mock_label.setFont(self.font_mock)
        self.mock_label.setStyleSheet("color: orange;")
        self.main_layout.addWidget(self.mock_label)

        self.media_label = QLabel()
        self.media_label.setAlignment(Qt.AlignCenter)
        self.media_label.setFixedHeight(300)  # Reduced from 400
        self.main_layout.addWidget(self.media_label)

        # Stretch before buttons (pushes them to bottom)
        self.main_layout.addStretch(1)

        # Navigation buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        buttons = [
            ("← Back", self.prev_tweet),
            ("Next →", self.next_tweet),
            ("Cancel Autoplay", self.stop_autoplay),
            ("Close", self.close)
        ]

        for text, slot in buttons:
            btn = QPushButton(text)
            btn.setFont(self.font_button)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1DA1F2;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #0d8ddb;
                }
            """)
            btn.clicked.connect(slot)
            button_layout.addWidget(btn)

        button_layout.addStretch(1)
        self.main_layout.addLayout(button_layout)

    def update_tweet(self, tweet):
        self.tweet_label.setText(tweet['text'])
        self.author_label.setText(f"@{tweet['author']}")
        self.time_label.setText(tweet.get("created_at", ""))

        qr_path = generate_qr_code(tweet['url'])
        self.qr_label.setPixmap(QPixmap(qr_path).scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.mock_label.setText("🧪 Mock Tweet" if tweet.get("mock", False) else "")

        media_urls = tweet.get("media", [])
        if media_urls:
            try:
                image_data = urlopen(media_urls[0]).read()
                image = QImage()
                image.loadFromData(image_data)
                pixmap = QPixmap(image)
                self.media_label.setPixmap(pixmap.scaledToHeight(300, Qt.SmoothTransformation))
            except Exception as e:
                print(f"❌ Failed to load media: {e}")
                self.media_label.clear()
        else:
            self.media_label.clear()

    def next_tweet(self):
        if self.on_next:
            self.on_next()

    def prev_tweet(self):
        if self.on_prev:
            self.on_prev()

    def stop_autoplay(self):
        if self.autoplay_timer and self.autoplay_timer.isActive():
            self.autoplay_timer.stop()
            print("⏸ Autoplay stopped.")
        else:
            print("⚠️ Autoplay already stopped or not set.")

    def closeEvent(self, event):
        if self.on_exit:
            self.on_exit()
        event.accept()
