import time
from html.parser import HTMLParser
from os import environ as env

import schedule
from dotenv import load_dotenv
from misskey import Misskey
from requests import get
from xmltodict import parse

load_dotenv()
misskey_domain = "koliosky.com"

mk = Misskey(misskey_domain, i = env["MISSKEY_TOKEN"])

class MyParser(HTMLParser):
    def handle_data(self, data):
        self.desc = data  # データを呼び出すときに呼ばれる

def job():
    print('発火')
    rss_url = "https://apod.nasa.gov/apod.rss" # RSSのURL
    response = get(rss_url) # RSSを取得
    parse_data = parse(response.text) # RSS(xml)をDict化

    parser = MyParser()
    parser.feed(parse_data['rss']['channel']['item'][1]['description']) # 説明文を取得

    mk.notes_create(f'TEST\n[今日のAPOD]({parse_data["rss"]["channel"]["item"][1]["link"]})\nTitle: {parse_data["rss"]["channel"]["item"][1]["title"]}\nDesc: {parser.desc}') # Misskeyにノートを送信

job()

'''schedule.every().day.at("12:00", "Asia/Tokyo").do(job)

# ずっと実行させるやつ(?)
while True:
    schedule.run_pending()
    time.sleep(1)'''