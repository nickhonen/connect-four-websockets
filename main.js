import { createBoard, playMove } from "./connect4.js";

function sendMoves(board, websocket) {
  // When clicking a column, send a "play" event for a move in that column.
  board.addEventListener("click", ({ target }) => {
    const column = target.dataset.column;
    // Ignore clicks outside a column.
    if (column === undefined) {
      return;
    }
    const event = {
      type: "play",
      column: parseInt(column, 10),
    };
    websocket.send(JSON.stringify(event));
  });
}

function showMessage(message) {
  // this is used because window.alert is synchronous, would screw up the game
  window.setTimeout(() => window.alert(message), 50);
}

function receiveMoves(board, websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "init":
        // Create link for inviting the second player.
        document.querySelector(".join").href = "?join=" + event.join;
        break;
      case "play":
        // update UI with move
        playMove(board, event.player, event.column, event.row);
        break;
      case "win":
        showMessage(`Player ${event.player} won!`);
        websocket.close(1000);
        break;
      case "error":
        showMessage(event.message);
        break;
      default:
        throw new Error(`Unknown event type: ${event.type}`);
    }
  });
}

function initGame(websocket) {
  websocket.addEventListener("open", () => {
    const params = new URLSearchParams(window.location.search);
    let event = { type: "init" };
    event.params = params;
    if (params.has("join")) {
      // if the person is clicking the join link, add join to event
      event.join = params.get("join");
    } else {
      // first player starts new game
    }
    websocket.send(JSON.stringify(event));
  });
}

function getServer() {
  // maybe shouldnt use hostname
  const url = window.location.hostname;
  if (url === "nickhonen.github.io") {
    return "wss://connect4-websockets.fly.dev/";
  } else if (url === "localhost") {
    return "ws://localhost:8080/";
  } else {
    throw new Error(`Unknown server: ${url}`);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  // Initialize the UI.
  const board = document.querySelector(".board");
  createBoard(board);
  // open websocket connection and register event handlers
  const websocket = new WebSocket(getServer());
  initGame(websocket);
  receiveMoves(board, websocket);
  sendMoves(board, websocket);
});

websocket.addEventListener("message", ({ data }) => {
  const event = JSON.parse(data);
  // do something with event
});
