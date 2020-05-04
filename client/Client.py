#!/usr/bin/env python

import asyncio
import websockets


class Client:
    def __init__(self, host, port):
        self.url = "ws://{}:{}".format(host, port)
        self.quit = False
        self.websocket = None

    async def start(self):
        self.websocket = await websockets.connect(self.url)
        messenger = asyncio.create_task(self.messenger())
        listener = asyncio.create_task(self.listener())
        await messenger
        listener.cancel()
        await self.websocket.close()
        print("Disconnected!")

    async def listener(self):
        try:
            while True:
                message = await self.websocket.recv()
                print('<< {}'.format(message))
        except websockets.ConnectionClosed:
            print("Error: Unexpected disconnection!")

    async def messenger(self):
        while not self.quit:
            message = input("> ")
            if message == 'quit':
                self.quit = True
            else:
                await self.websocket.send(message)


if __name__ == '__main__':
    host = input("Enter host address: ")
    port = input("Enter host port: ")
    cli = Client(host, port)
    asyncio.get_event_loop().run_until_complete(cli.start())
