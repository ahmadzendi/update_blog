import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta, timezone
import os

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

URL = 'https://blog.indodax.com/en_US/newsroom-latest-stories'
LAST_POST_FILE = 'last_post.json'

def get_latest_post():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    article = soup.find('article', class_='eael-grid-post')
    if article:
        h2 = article.find('h2', class_='eael-entry-title')
        if h2:
            link = h2.find('a', class_='eael-grid-post-link', href=True)
            if link:
                return {
                    'url': link['href'],
                    'title': link.get_text(strip=True)
                }
    return None

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': message,
        'disable_web_page_preview': False
    }
    requests.post(url, data=data)

def load_last_post():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r') as f:
            return json.load(f).get('last_post')
    return None

def save_last_post(post_url):
    with open(LAST_POST_FILE, 'w') as f:
        json.dump({'last_post': post_url}, f)

def main():
    while True:
        latest_post = get_latest_post()
        last_post = load_last_post()
        if latest_post and latest_post['url'] != last_post:
            wib = timezone(timedelta(hours=7))
            now = datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S')
            message = f"Update terbaru di Indodax Newsroom:\n\n{latest_post['title']}\n{latest_post['url']}\n\nWaktu update (WIB): {now}"
            send_telegram_message(message)
            save_last_post(latest_post['url'])
            print("Notifikasi dikirim:", latest_post['title'])
        else:
            print("Belum ada update baru.")
        time.sleep(300) # Cek setiap 5 menit

if __name__ == '__main__':
    main()
