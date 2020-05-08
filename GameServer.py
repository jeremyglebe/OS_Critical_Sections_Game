#!/usr/bin/env python

import asyncio
import sys
import websockets
from collections import deque
from math import floor
from random import random, choice

# Constants used for testing mostly
MAX_SIZE = sys.maxsize  # Maximum value, positive and negative, to make key
WAIT_TIME = 1  # Time to wait per cycle of the lock manager
FAKE_LOCK_CHANCE = 33  # Percentage chance each cycle for a fake locking

# Set of connected clients
clients = set()
# Lock is set to None when unlocked, and set to a websocket when locked for
# that socket's use
lock = None
# Queue of clients wanting to acquire the lock
lock_queue = deque()
# Number the clients need to guess
secret_key = floor(random() * MAX_SIZE) * choice((1, -1))


async def connection(websocket, path):
    '''Handler for a client connecting'''
    # Get globals
    global lock
    global secret_key
    # Add the connecting websocket to the clients list
    clients.add(websocket)
    try:
        # For every message that the client sends
        async for message in websocket:
            try:
                # Try to parse the message as a number
                # (numbers are guesses, other messages may have special meanings)
                guess = int(message)
                # Make sure that the guesser has the lock
                if lock is websocket:
                    # Check the correctness of the guess
                    if guess == secret_key:
                        await websocket.send('0')
                        print("Client guessed the key!")
                        secret_key = floor(
                            random() * MAX_SIZE) * choice((1, -1))
                        print(
                            "The secret number is {}. Sssshhh...".format(secret_key))
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
    # Release the lock if the disconnected client is holding it
    if lock is websocket:
        lock = None


async def lock_manager():
    global lock
    while True:
        # Every second, process the current status of the lock
        await asyncio.sleep(WAIT_TIME)
        # If the lock is available, we may arbitrarily lock it as part of the
        # simulation.
        if lock == None:
            if floor((random() * 100) + 1) <= FAKE_LOCK_CHANCE:
                lock = 'fake_client'
            else:
                if len(lock_queue) > 0:
                    lock = lock_queue.popleft()
                    print("Sending lock acquired")
                    await lock.send('lock acquired')
        elif lock == 'fake_client':
            lock = None
        print(f'Lock: {lock}')

if __name__ == '__main__':
    try:
        # Print the initial secret number
        print("The secret number is {}. Sssshhh...".format(secret_key))
        # Run the server
        server_start = websockets.serve(connection, "localhost", 8080)
        asyncio.get_event_loop().run_until_complete(server_start)
        # Run the lock manager until manually closed
        asyncio.get_event_loop().run_until_complete(lock_manager())

        # If the code above does not run infinitely, we can prevent the server
        # from closing with run_forever
        # asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\rServer closed by keypress...")
    # Close the server
    server_start.ws_server.close()
