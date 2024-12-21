#!/usr/bin/env python
import json
import asyncio

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK
from connect4 import PLAYER1, PLAYER2, Connect4

async def handler(websocket):
    for player, column, row in [
        (PLAYER1, 3, 0),
        (PLAYER2, 3, 1),
        (PLAYER1, 4, 0),
        (PLAYER2, 4, 1),
        (PLAYER1, 2, 0),
        (PLAYER2, 1, 0),
        (PLAYER1, 5, 0),
    ]:
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))
        # 7 moves appear at .5 second intervals.
        await asyncio.sleep(.5)
    # async for message in websocket:
    #     try:
    #         print(message)
    #     except ConnectionClosedOK:
    #         print("Connection closed.")
    #         break



async def main():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())