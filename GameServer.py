#!/usr/bin/env python

import asyncio
import websockets

clients = set()

async def connection_handler(websocket, path):
    clients.add(websocket)
    try:
        while True:
            message = await websocket.recv()
            for ws in clients:
                if ws is not websocket:
                    try:
                        await ws.send(message)
                    except websockets.ConnectionClosed:
                        print("Tried to send message to disconnected client!")
            print(message)
    except websockets.ConnectionClosed:
        print("Client disconnected...")
    clients.remove(websocket)

async def echo(websocket, path):
    async for message in websocket:
        print(message)
        await websocket.send(message)

# async def connection(websocket, path):
#     async for message in websocket:


# Create the server connection handler
listen = websockets.serve(connection_handler, "localhost", 8080)
# Run the server
asyncio.get_event_loop().run_until_complete(listen)
asyncio.get_event_loop().run_forever()
