from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import scratchattach as sa
import asyncio
import os

scratch_password = os.getenv('SCRATCH_PASSWORD')

# 非同期でScratchの通知リスナーを開始する関数
async def start_scratch_listener():
    # sa.login()は同期関数なので、非同期でラップする
    session = await asyncio.to_thread(sa.login, "Zei_Para_channel", scratch_password)
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
        asyncio.create_task(send_notifications_to_clients(notification))

    events.start()

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

# WebSocketクライアントに通知を送信
async def send_notifications_to_clients(notification):
    for client in clients:
        await client.send_json(notification)

# サーバー起動時にScratch通知リスナーを開始
@app.on_event("startup")
async def startup_event():
    # 非同期関数をawaitで呼び出す
    await start_scratch_listener()

# FastAPIアプリケーションを起動
app = FastAPI()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Render.comで指定されたポートを使用
    uvicorn.run("main:app", host="0.0.0.0", port=port)
