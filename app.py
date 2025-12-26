import socketio
from fastapi import FastAPI
import uvicorn
import random
import os

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)

app = FastAPI()
sio_app = socketio.ASGIApp(sio, app)

waiting_users = []

@sio.event
async def connect(sid, environ):
    print("User connected:", sid)

@sio.event
async def start(sid):
    if sid not in waiting_users:
        waiting_users.append(sid)

    if len(waiting_users) >= 2:
        u1 = waiting_users.pop(0)
        u2 = waiting_users.pop(0)

        room = str(random.randint(1000, 9999))
        await sio.enter_room(u1, room)
        await sio.enter_room(u2, room)

        await sio.emit("matched", {"room": room, "initiator": True}, to=u1)
        await sio.emit("matched", {"room": room, "initiator": False}, to=u2)

@sio.event
async def signal(sid, data):
    await sio.emit("signal", data, room=data["room"], skip_sid=sid)

@sio.event
async def next(sid):
    await start(sid)

@sio.event
async def disconnect(sid):
    if sid in waiting_users:
        waiting_users.remove(sid)
    print("Disconnected:", sid)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(sio_app, host="0.0.0.0", port=port)
