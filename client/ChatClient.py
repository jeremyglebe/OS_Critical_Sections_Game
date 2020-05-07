#!/usr/bin/env python
'''Client for a chat program. I wrote this to test websockets. It is not needed
but I don't really want to delete it yet because it makes a good reference.'''
import asyncio
import websockets

websocket = None


async def start(url):
    global websocket
    websocket = await websockets.connect(url)
    messenger_task = asyncio.create_task(messenger())
    listener_task = asyncio.create_task(listener())
    await messenger_task
    listener_task.cancel()
    await websocket.close()
    print("Disconnected!")


async def listener():
    try:
        while True:
            message = await websocket.recv()
            print('\r<< {}\n> '.format(message), end='')
    except websockets.ConnectionClosed:
        print("Error: Unexpected disconnection!")


async def messenger():
    messenger_done = False
    while not messenger_done:
        message = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
        if message == 'quit':
            messenger_done = True
        else:
            await websocket.send(message)


if __name__ == '__main__':
    # Get the server to connect to
    host = input("Enter host address: ")
    port = input("Enter host port: ")
    url = "ws://{}:{}".format(host, port)
    asyncio.get_event_loop().run_until_complete(start(url))
