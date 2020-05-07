#!/usr/bin/env python

import asyncio
import websockets

clients = set()


async def old_handler(websocket, path):
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


async def connection(websocket, path):
    clients.add(websocket)
    try:
        async for message in websocket:
            print(message)
    except websockets.ConnectionClosed:
        print("Client disconnected...")
    except KeyboardInterrupt:
        print("Server closed by keypress...")
    except:
        print("An unexpected error occured!")
    clients.remove(websocket)


if __name__ == '__main__':
    try:
        # Create the server connection handler
        server_start = websockets.serve(connection, "localhost", 8080)
        # Run the server
        asyncio.get_event_loop().run_until_complete(server_start)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\rServer closed by keypress...")
    except:
        print("An unexpected error occured!")
