#!/usr/bin/env python

import asyncio

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK

async def handler(websocket):
    async for message in websocket:
        try:
            print(message)
        except ConnectionClosedOK:
            print("Connection closed.")
            break



async def main():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())