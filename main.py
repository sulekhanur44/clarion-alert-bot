import os
import requests
from bs4 import BeautifulSoup
import time
from flask import Flask
from threading import Thread

# ============== SETUP (Now using environment variables) ==============
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MOVINGSOON_URL = "https://movingsoon.co.uk/housing-association/clarion-housing/"
seen = set()

# ============== TELEGRAM ALERT ==============
def send_alert(title, url):
    text = f"\U0001F3E0 New Clarion listing:\n{title}\n{url}"
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": text}
    )
    print("\U0001F4E8 Sent alert:", title)

# ============== WEB SCRAPER ==============
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

# ============== FLASK SERVER ==============
app = Flask('')

@app.route('/')
def home():
    return "\u2705 Clarion bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

# ============== SELF-PING FUNCTION ==============
def self_ping():
    while True:
        try:
            requests.get("https://clarion-alert-bot.onrender.com")  # Update if URL changes
        except:
            pass
        time.sleep(60)

# ============== START SERVER + SELF-PING ==============
Thread(target=run).start()
Thread(target=self_ping).start()

# ============== MAIN BOT LOOP ==============
print("\U0001F916 Bot started...")
while True:
    try:
        new_listings = get_listings()
        for title, url in new_listings:
            send_alert(title, url)
        print("\u2705 Checked for new listings.")
    except Exception as e:
        print("\u26A0\uFE0F Error:", e)
    time.sleep(60)
