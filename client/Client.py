#!/usr/bin/env python

import asyncio
import websockets
from random import random
from math import floor


class Client:
    def __init__(self):
        self.guess_mode = 0
        self.websocket = None

    def set_mode(self, guess_mode):
        self.guess_mode = guess_mode

    async def connect(self, host, port):
        url = "ws://{}:{}".format(host, port)
        self.websocket = await websockets.connect(url)
        await self.start()

    async def start(self):
        try:
            while True:
                if self.guess_mode == 0:
                    await self.guess_random()
                await asyncio.sleep(1)
        except websockets.ConnectionClosed:
            print("Disconnected from server...")

    async def guess_random(self):
        guess = floor(random() * 100)
        await self.websocket.send(str(guess))

    async def listen_echo(self):
        try:
            async for message in self.websocket:
                print(message)
        except websockets.ConnectionClosed:
            print("Error: Unexpected disconnection!")


if __name__ == '__main__':
    # Get the server to connect to
    host = input("Enter host address: ")
    port = input("Enter host port: ")
    # Create a client object
    cli = Client()
    asyncio.get_event_loop().run_until_complete(cli.connect(host, port))
