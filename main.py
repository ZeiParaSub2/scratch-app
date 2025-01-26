from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import scratchattach as sa
import asyncio
import os

async def start_scratch_listener():
    # 非同期処理をここに書く
    session = sa.login("your_username", "your_password")
    # 他の非同期処理もここで行うことができます
    await some_async_task()

scratch_password = os.getenv('SCRATCH_PASSWORD')

app = FastAPI()

# 通知データ保存用（テスト用に簡易リストを使用、DBに保存も可能）
notifications = []

# WebSocketで接続しているクライアントを保持
clients = []

# 通知データのモデル
class Notification(BaseModel):
    title: str
    message: str

# WebSocketエンドポイント（リアルタイム通知用）
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # 無限ループで接続維持
    except Exception as e:
        print(f"WebSocket切断: {e}")
    finally:
        clients.remove(websocket)

# Scratchattachで通知を感知する
def start_scratch_listener():
    session = sa.login("Zei_Para_channel", scratch_password)
    events = session.connect_message_events()

    @events.event
    def on_message(message):
        # 新しい通知をリストに保存
        notification = {
            "title": f"新しい通知 from {message.actor_username}",
            "message": f"{message.actor_username} sent a {message.type}"
        }
        notifications.append(notification)

        # WebSocketで接続している全クライアントに通知を送る
        asyncio.run(send_notifications_to_clients(notification))

    events.start()

# WebSocketクライアントに通知を送信
async def send_notifications_to_clients(notification):
    for client in clients:
        await client.send_json(notification)

# サーバー起動時にScratch通知リスナーを開始
@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(start_scratch_listener())
