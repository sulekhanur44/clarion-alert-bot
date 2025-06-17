import requests
from bs4 import BeautifulSoup
import time
from flask import Flask
from threading import Thread

# ========== SETUP ==========
TELEGRAM_BOT_TOKEN = "8191093355:AAHopcy7mOTVOX5d9EIoseCIIDm-K5DbbLg"
TELEGRAM_CHAT_ID = "7958138108"
MOVINGSOON_URL = "https://movingsoon.co.uk/housing-association/clarion-housing/"
seen = set()

# ========== TELEGRAM ALERT ==========
def send_alert(title, url):
    text = f"🏠 New Clarion listing:\n{title}\n{url}"
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": text}
    )
    print("📨 Sent alert:", title)

# ========== SCRAPER ==========
def get_listings():
    response = requests.get(MOVINGSOON_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    listings = soup.select(".property-content h2 a")
    new = []
    for item in listings:
        url = item['href']
        title = item.get_text(strip=True)
        if url not in seen:
            seen.add(url)
            new.append((title, url))
    return new

# ========== FLASK SERVER ==========
app = Flask('')
@app.route('/')
def home():
    return "✅ Clarion bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

# ========== SELF PING ==========
def self_ping():
    while True:
        try:
            requests.get("https://clarion-alert-bot.onrender.com")
        except:
            pass
        time.sleep(60)

# ========== START SERVICES ==========
Thread(target=run).start()
Thread(target=self_ping).start()

# ========== MAIN LOOP ==========
print("🤖 Bot started...")
while True:
    try:
        for title, url in get_listings():
            send_alert(title, url)
        print("✅ Checked for new listings.")
    except Exception as e:
        print("⚠️ Error:", e)
    time.sleep(60)
