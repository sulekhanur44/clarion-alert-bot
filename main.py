import requests
from bs4 import BeautifulSoup
import time
from flask import Flask
from threading import Thread

TELEGRAM_BOT_TOKEN = "8191...bbLg"
TELEGRAM_CHAT_ID = "7958..."
MOVINGSOON_URL = "https://movingsoon.co.uk/housing-association/clarion-housing/"
seen = set()

def send_alert(title, url):
    text = f"🏠 New Clarion listing:\n{title}\n{url}"
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": text}
    )
    print("📨 Sent alert:", title)

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

app = Flask('')
@app.route('/')
def home():
    return "✅ Clarion bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run).start()

print("🤖 Bot started...")
send_alert("🧪 TEST: Clarion bot is working!", "https://example.com/test-listing")
while True:
    try:
        for t, u in get_listings():
            send_alert(t, u)
        print("✅ Checked for new listings.")
    except Exception as e:
        print("⚠️ Error:", e)
    time.sleep(60)
