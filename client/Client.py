#!/usr/bin/env python

import asyncio
import websockets


class Client:
    def __init__(self, host, port):
        self.url = "ws://{}:{}".format(host, port)
        self.quit = False

    async def start(self):
        async with websockets.connect(self.url) as websocket:
            messenger = asyncio.create_task(self.send(websocket))
            listener = asyncio.create_task(self.listen(websocket))
            await messenger
        listener.cancel()
        print("Disconnected!")

    async def listen(self, websocket):
        async for message in websocket:
            print('<< {}'.format(message))

    async def send(self, websocket):
        while not self.quit:
            message = input("> ")
            if message == 'quit':
                self.quit = True
            else:
                await websocket.send(message)


if __name__ == '__main__':
    host = input("Enter host address: ")
    port = input("Enter host port: ")
    cli = Client(host, port)
    asyncio.get_event_loop().run_until_complete(cli.start())
