import os
import requests
from bs4 import BeautifulSoup
import time
from flask import Flask
from threading import Thread

# ============== SETUP ==============
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MOVINGSOON_URL = "https://movingsoon.co.uk/housing-association/clarion-housing/"
seen = set()

# ============== TELEGRAM ALERT ==============
def send_alert(title, url):
    text = f"🏠 New Clarion listing:\n{title}\n{url}"
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": text}
    )
    print("📨 Sent alert:", title)

# ============== WEB SCRAPER ==============
def get_listings():
    rsp = requests.get(MOVINGSOON_URL)
    soup = BeautifulSoup(rsp.text, "html.parser")
    items = soup.select(".property-content h2 a")
    new = []
    for itm in items:
        url = itm['href']
        title = itm.get_text(strip=True)
        if url not in seen:
            seen.add(url)
            new.append((title, url))
    return new

# ============== FLASK SERVER ==============
app = Flask('')
@app.route('/')
def home():
    return "✅ Clarion bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

# ============== KEEP RENDER ALIVE ==============
def self_ping():
    while True:
        try:
            requests.get("https://clarion-alert-bot.onrender.com")
        except:
            pass
        time.sleep(60)

# ============== START SERVER + SELF-PING ==============
Thread(target=run).start()
Thread(target=self_ping).start()

# ============== OPTIONAL TEST ALERT ==============
if os.environ.get("RUN_TEST") == "true":
    send_alert("🧪 Test Alert", "https://example.com/test")

# ============== MAIN BOT LOOP ==============
print("🤖 Bot started...")
while True:
    try:
        for t, u in get_listings():
            send_alert(t, u)
        print("✅ Checked for new listings.")
    except Exception as e:
        print("⚠️ Error:", e)
    time.sleep(60)
