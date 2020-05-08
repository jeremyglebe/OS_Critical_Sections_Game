#!/usr/bin/env python

import asyncio
import websockets
from random import random, choice
from math import floor


class Client:
    def __init__(self):
        # We store guess (instead of just sending it and moving on) so we can
        # print it alongside the response from the server
        self.current_guess = None
        # Guess mode determines what guessing strategy we will use
        self.guess_mode = 0
        # This is the socket connection to the server
        self.websocket = None

    def set_mode(self, guess_mode):
        self.guess_mode = guess_mode

    async def connect(self, host, port):
        url = "ws://{}:{}".format(host, port)
        self.websocket = await websockets.connect(url)
        guess_task = asyncio.create_task(self.guess())
        response_task = asyncio.create_task(self.listen_response())
        await guess_task
        response_task.cancel()
        await self.websocket.close()
        print("Disconnected!")

    async def guess(self):
        try:
            while True:
                if self.guess_mode == 0:
                    await self.guess_random()
                await asyncio.sleep(1)
        except websockets.ConnectionClosed:
            print("Disconnected from server...")

    async def guess_random(self):
        self.current_guess = floor(random() * 10) * choice((-1,1))
        await self.websocket.send(str(self.current_guess))

    async def listen_response(self):
        try:
            async for message in self.websocket:
                if message == '-1':
                    print(f"{self.current_guess} is too low!")
                elif message == '1':
                    print(f"{self.current_guess} is too high!")
                elif message == '0':
                    print(f"You guessed the key, {self.current_guess}!")
        except websockets.ConnectionClosed:
            print("Error: Unexpected disconnection!")


if __name__ == '__main__':
    try:
        # Get the server to connect to
        host = input("Enter host address: ")
        port = input("Enter host port: ")
        # Create a client object
        cli = Client()
        asyncio.get_event_loop().run_until_complete(cli.connect(host, port))
    except KeyboardInterrupt:
        print("\rClient closed by keypress...")
