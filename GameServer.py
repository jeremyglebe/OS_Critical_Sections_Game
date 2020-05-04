#!/usr/bin/env python

import asyncio
import websockets

clients = set()

async def connection_handler(websocket, path):
    clients.add(websocket)
    async for message in websocket:
        print(clients)
        for ws in clients:
            if ws is not websocket:
                await ws.send(message)
        print(message)
    clients.remove(websocket)

listen = websockets.serve(connection_handler, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(listen)
asyncio.get_event_loop().run_forever()
