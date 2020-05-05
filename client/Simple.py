#!/usr/bin/env python

import asyncio
import datetime
import websockets


async def start_client(host, port):
    url = "ws://{}:{}".format(host, port)
    async with websockets.connect(url) as websocket:
        while True:
            await websocket.send(datetime.datetime.now().isoformat())
            print(await websocket.recv())
            await asyncio.sleep(1)


if __name__ == '__main__':
    host = input("Enter host address: ")
    port = input("Enter host port: ")

    asyncio.get_event_loop().run_until_complete(start_client(host, port))
