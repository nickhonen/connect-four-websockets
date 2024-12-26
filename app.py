#!/usr/bin/env python
import json
import asyncio
import logging
import itertools
import secrets

from websockets.asyncio.server import serve, broadcast
from websockets.exceptions import ConnectionClosedOK
from connect4 import PLAYER1, PLAYER2, Connect4

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

JOIN = {}

async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))

async def play(websocket, game, player, connected):
    turns = itertools.cycle([PLAYER1, PLAYER2])
    player = next(turns)

    async for message in websocket:
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"]

        try:
            row = game.play(player, column)
        except ValueError as exc:
            # send error message to client
            await error(websocket, str(exc))
            continue
    
        # Send a "play" event to update the UI
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        broadcast(connected, json.dumps(event))
       
        # if move wins, send win event
        if game.winner is not None:    
            event = {
                "type": "win",
                "player": game.winner,
            }
            await websocket.send(json.dumps(event))

        # iterate list
        player = next(turns)


async def start(websocket):
    game = Connect4()
    # set of websocket connections receiving moves from this game
    connected = {websocket}
    # TODO: lookup what this does
    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected
    
    try:
        # send secret access to first players browser
        # make a join link
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))
        await play(websocket, game, PLAYER1, connected)

        # temporary test lines
        print("first player starts game", id(game)) 

    finally:
        del JOIN[join_key]

async def join(websocket, join_key):
    # Find the Connect Four game.
    try:
        game, connected = JOIN[join_key]

    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:

        # Temporary - for testing.
        print("second player joined game", id(game))
        await play(websocket, game, PLAYER2, connected)

    finally:
        connected.remove(websocket)

async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # second player joins game
        await join(websocket, event["join"])
    else:
        # first player starts a new game.
        await start(websocket)



    



# async def handler(websocket):
#     # initalize game
#     game = Connect4()

#     # taking alternate turns with same browser,
#     # TODO: implement this without itertools to understand the code
#     turns = itertools.cycle([PLAYER1, PLAYER2])
#     player = next(turns)

#     async for message in websocket:
#         event = json.loads(message)
#         assert event["type"] == "play"
#         column = event["column"]

#         try:
#             row = game.play(player, column)
#         except ValueError as exc:
#             # send error message to client
#             event = {
#                 "type": "error",
#                 "message": str(exc),
#             }
#             await websocket.send(json.dumps(event))
#             continue
    
#         # Send a "play" event to update the UI
#         event = {
#             "type": "play",
#             "player": player,
#             "column": column,
#             "row": row,
#         }
#         await websocket.send(json.dumps(event))
       
#         # if move wins, send win event
#         if game.winner is not None:    
#             event = {
#                 "type": "win",
#                 "player": game.winner,
#             }
#             await websocket.send(json.dumps(event))

#         # iterate list
#         player = next(turns)



async def main():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())