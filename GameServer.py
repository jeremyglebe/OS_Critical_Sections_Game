#!/usr/bin/env python

import asyncio
import sys
import websockets
from collections import deque
from math import floor
from random import random, choice

# Constants used for testing mostly
MAX_SIZE = sys.maxsize

# Set of connected clients
clients = set()
# Lock is set to None when unlocked, and set to a websocket when locked for
# that socket's use
lock = None
# Queue of clients wanting to acquire the lock
lock_queue = deque()
# Number the clients need to guess
secret_key = floor(random() * MAX_SIZE) * choice((1,-1))

# Handler for a client connecting
async def connection(websocket, path):
    # Get globals
    global lock
    global secret_key
    # Add the connecting websocket to the clients list
    clients.add(websocket)
    try:
        # For every message that the client sends
        async for message in websocket:
            # Try to parse the message as a number
            # (numbers are guesses, other messages may have special meanings)
            try:
                guess = int(message)
                if guess == secret_key:
                    await websocket.send('0')
                    print("Client guessed the key!")
                    secret_key = floor(random() * MAX_SIZE) * choice((1,-1))
                    print("The secret number is {}. Sssshhh...".format(secret_key))
                elif guess < secret_key:
                    await websocket.send('-1')
                else:
                    await websocket.send('1')
            except:
                # The message is not a guess, so let's check special messages
                # If the client wants the lock, queue them up
                if message == "request lock" and websocket not in lock_queue:
                    lock_queue.append(websocket)
                # If the client with the lock is releasing it, unlock
                elif message == "release lock" and lock is websocket:
                    lock = None
    # When the client disconnects
    except websockets.ConnectionClosed:
        print("Client disconnected...")
    # Once all messages have been processed (the client is disconnected)
    # Remove the websocket from the set of connected clients
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
