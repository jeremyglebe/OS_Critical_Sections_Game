#!/usr/bin/env python

import asyncio
import sys
import websockets
from math import floor
from random import random, choice

clients = set()
# secret_key = floor(random() * sys.maxsize) * choice((1,-1))
secret_key = floor(random() * 10) * choice((1,-1))

async def connection(websocket, path):
    global secret_key
    clients.add(websocket)
    try:
        async for message in websocket:
            guess = int(message)
            if guess == secret_key:
                await websocket.send('0')
                print("Client guessed the key!")
                # secret_key = floor(random() * sys.maxsize) * choice((1,-1))
                secret_key = floor(random() * 10) * choice((1,-1))
                print("The secret number is {}. Sssshhh...".format(secret_key))
            elif guess < secret_key:
                await websocket.send('-1')
            else:
                await websocket.send('1')
    except websockets.ConnectionClosed:
        print("Client disconnected...")
    except KeyboardInterrupt:
        print("Server closed by keypress...")
    clients.remove(websocket)


if __name__ == '__main__':
    try:
        # Print the initial secret number
        print("The secret number is {}. Sssshhh...".format(secret_key))
        # Create the server connection handler
        server_start = websockets.serve(connection, "localhost", 8080)
        # Run the server
        asyncio.get_event_loop().run_until_complete(server_start)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\rServer closed by keypress...")
