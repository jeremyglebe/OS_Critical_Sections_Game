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

    async def connect(self, host, port):
        url = "ws://{}:{}".format(host, port)
        self.websocket = await websockets.connect(url)
        print("got connected")
        guess_task = asyncio.create_task(self.guess())
        await guess_task
        await self.websocket.close()
        print("Disconnected!")

    async def guess(self):
        try:
            while True:
                # The client needs to acquire a lock with the server before it
                # can proceed
                # Request the lock
                await self.websocket.send('request lock')
                # Wait to acquire the lock
                resp = ''
                while not resp == 'lock acquired':
                    resp = await self.websocket.recv()

                # The client should attempt a guess once it has acquired a lock
                if self.guess_mode == 0:
                    await self.guess_random()

                # Once a guess has been made, we need to wait for a response
                # from the server
                guess_resp = await self.websocket.recv()
                # Print the information regarding the guess response
                if guess_resp == '-1':
                    print(f"{self.current_guess} is too low!")
                elif guess_resp == '1':
                    print(f"{self.current_guess} is too high!")
                elif guess_resp == '0':
                    print(f"You guessed the key, {self.current_guess}!")

                # Once the client has successfully guessed, it should release the lock
                await self.websocket.send('release lock')

                # Wait a moment between guesses
                await asyncio.sleep(1)
        except websockets.ConnectionClosed:
            print("Disconnected from server...")

    async def guess_random(self):
        self.current_guess = floor(random() * 10) * choice((-1, 1))
        await self.websocket.send(str(self.current_guess))

    def set_mode(self, guess_mode):
        self.guess_mode = guess_mode

    def start(self):
        asyncio.get_event_loop().run_until_complete(self.connect(host, port))


if __name__ == '__main__':
    try:
        # Get the server to connect to
        host = input("Enter host address: ")
        port = input("Enter host port: ")
        # Create a client object
        cli = Client()
        cli.start()
    except KeyboardInterrupt:
        print("\rClient closed by keypress...")
