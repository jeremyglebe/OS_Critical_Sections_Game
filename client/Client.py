#!/usr/bin/env python

import asyncio
import websockets
from random import random, randrange, choice
from math import floor

# Constants used for testing mostly
WAIT_TIME = 0.01  # Time to wait per guess
PRINT_TIME = 2.5  # Time to wait per cycle of the printer


class Client:
    def __init__(self):
        # We store guess (instead of just sending it and moving on) so we can
        # print it alongside the response from the server
        self.current_guess = None
        # Guess mode determines what guessing strategy we will use
        self.guess_mode = 0
        # This is the socket connection to the server
        self.websocket = None
        # Variables to assist with guessing strategies
        self.lower_bound = None
        self.upper_bound = None

    async def connect(self, host, port):
        url = "ws://{}:{}".format(host, port)
        self.websocket = await websockets.connect(url)
        print("Connected!")
        guess_task = asyncio.create_task(self.guess())
        print_task = asyncio.create_task(self.printer())
        await guess_task
        print_task.cancel()
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
                    await self.bounded_guess()

                # Once the client has successfully guessed, it should release the lock
                await self.websocket.send('release lock')

                # Wait a moment between guesses
                await asyncio.sleep(WAIT_TIME)
        except websockets.ConnectionClosed:
            print("Disconnected from server...")

    async def guess_random(self):
        self.current_guess = floor(random() * 10) * choice((-1, 1))
        await self.websocket.send(str(self.current_guess))

    async def bounded_guess(self):
        # Determine a guess based on upper/lower bounds
        # If we don't yet have bounds, make a guess between -1M and +1M
        if self.upper_bound == None and self.lower_bound == None:
            self.current_guess = floor(random() * 1000000) * choice((-1, 1))
        # If there exists a lower bound but no upper bound, make a guess
        # between LB and LB+2M
        elif self.upper_bound == None:
            self.current_guess = self.lower_bound + 2000000
        # If there exists an upper bound but no lower bound, make a guess
        # between UB - 2M and UB
        elif self.lower_bound == None:
            self.current_guess = self.upper_bound - 2000000
        # If bounds are the same, then someone else solved the number already and we missed it
        elif self.lower_bound == self.upper_bound:
            self.lower_bound = None
            self.upper_bound = None
        # If both bounds exist, pick a value between the two
        else:
            self.current_guess = randrange(self.lower_bound, self.upper_bound + 1)

        # Send the guess
        await self.websocket.send(str(self.current_guess))
        # Once a guess has been made, we need to wait for a response
        # from the server
        guess_resp = await self.websocket.recv()
        # Print the information regarding the guess response
        if guess_resp == '-1':
            # Maybe update the lower bound
            if self.lower_bound == None or self.current_guess > self.lower_bound:
                self.lower_bound = self.current_guess
        elif guess_resp == '1':
            # Maybe update the upper bound
            if self.upper_bound == None or self.current_guess < self.upper_bound:
                self.upper_bound = self.current_guess
        elif guess_resp == '0':
            print(f"You guessed the key, {self.current_guess}!")
            self.upper_bound = None
            self.lower_bound = None

    async def printer(self):
        while True:
            await asyncio.sleep(PRINT_TIME)
            print(f"Bounds: {self.lower_bound}L, {self.upper_bound}H")

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
