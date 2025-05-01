// Simple WebSocket test client for /stream endpoint
const WebSocket = require("ws");

const ws = new WebSocket("ws://localhost:8000/ws");

ws.on("open", function open() {
  // Send a sample message (replace with your actual input structure)
  ws.send(
    JSON.stringify({
      messages: "I'd like to plan meals for the weekend, for two persons",
    })
  );
});

ws.on("message", function message(data) {
  console.log("Received:", data.toString());
});

ws.on("close", function close() {
  console.log("Connection closed");
});

ws.on("error", function error(err) {
  console.error("WebSocket error:", err);
});
