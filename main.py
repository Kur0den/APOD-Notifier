import asyncio
import json
import time
from html.parser import HTMLParser
from os import environ as env

import schedule
import websockets
from dotenv import load_dotenv
from misskey import Misskey
from requests import get
from xmltodict import parse

load_dotenv()
misskey_domain = "koliosky.com"


mk = Misskey(misskey_domain, i = env["MISSKEY_TOKEN"])
mk_id = mk.i()['id']
ws_url = f'wss://{misskey_domain}/streaming?i={env["MISSKEY_TOKEN"]}'
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

    mk.notes_create(f'[今日のAPOD]({parse_data["rss"]["channel"]["item"][1]["link"]})\nTitle: {parse_data["rss"]["channel"]["item"][1]["title"]}\nDesc: {parser.desc}') # Misskeyにノートを送信

schedule.every().day.at("12:00", "Asia/Tokyo").do(job) # 12:00にRSS取得+投稿を実行するようにスケジュールを登録

async def trigger():# スケジュールずっと実行させるやつ
    while True:
        schedule.run_pending()
        time.sleep(1)

async def runner(): # 生存確認用(Misskey上でメンションしたら反応するやつ)
    asyncio.create_task(trigger()) # スケジュール用の無限ループ実行
    async with websockets.connect(ws_url) as ws: # type: ignore  ##websocketに接続
        await ws.send(json.dumps({
            'type': 'connect',
            'body': {
                'channel': 'main',
                'id': '1'
            } # mainチャンネルに接続
        }))
        while True:
            msg = json.loads(await ws.recv())
            if msg['body']['type'] == 'mention': # メンション時に反応
                print('ping')
                note_id = msg['body']['body']['id']
                user_name = msg['body']['body']['user']['username']
                user_host = msg['body']['body']['user']['host']
                if user_host == None:
                    mk.notes_create(text=f'@{user_name} Pong!', reply_id=note_id) # Pong!
                else:
                    mk.notes_create(text=f'@{user_name}@{user_host} Pong!', reply_id=note_id) # Pong!



print('ready')
asyncio.get_event_loop().run_until_complete(runner()) # runner()を実行