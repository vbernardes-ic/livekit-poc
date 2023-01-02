import WebSocket, { WebSocketServer } from "ws";
const wss = new WebSocketServer({ port: 8080 });
console.log("wss.js")

wss.on("connection", function connection(ws) {
    console.log("connection");

    // Connect to rev.ai websocket api
    // send binary data
    const rev_ai_conn = new WebSocket('ws://www.rev.ai/path');
    rev_ai_conn.on('open', function open() {
        console.log("Connection with rev.ai estabilished")
    });

    // Messages sent from Egress
    ws.on("message", function message(data) {
        console.log("received: %s", data);


        rev_ai_conn.send(array);
    });

    // Messages sent from rev.ai
    rev_ai_conn.on('message', function message(data) {
        console.log('received: %s', data);
    });
});
