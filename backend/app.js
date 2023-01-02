import express from "express";
import { AccessToken, EgressClient, RoomServiceClient, WebhookReceiver } from "livekit-server-sdk";
import cors from "cors";
import bodyParser from "body-parser";



const livekitHost = "ws://localhost:7880"
const svc = new RoomServiceClient(livekitHost, "devkey", "secret")
const receiver = new WebhookReceiver("devkey", "secret");
const egressClient = new EgressClient(
  livekitHost,
  'devkey',
  'secret'
);

const app = express();
const port = 3001;



app.use(cors());

app.get("/get-token", (req, res) => {
    // if this room doesn't exist, it'll be automatically created when the first
    // client joins
    const roomName = "my-room";
    // identifier to be used for participant.
    // it's available as LocalParticipant.identity with livekit-client SDK
    console.log(req.query.username);

    const participantName = req.query.username;

    const at = new AccessToken("devkey", "secret", {
        identity: participantName,
    });
    at.addGrant({ roomJoin: true, room: roomName });

    const token = at.toJwt();
    console.log("access token", token);

    svc.listRooms().then((rooms) => {
      console.log('existing rooms', rooms);
    });

    res.send({ token, user: participantName });

});

app.post('/webhooks', bodyParser.raw({type: "application/webhook+json"}), async (req, res) => {
  // event is a WebhookEvent object
  const event = receiver.receive(req.body, req.get('Authorization'))

  if (event.event === "track_published") {
    console.log("======track_published=====")
    const info = await egressClient.startTrackEgress(
      'my-room',
      'ws://192.168.65.2:8080',
      event.track.sid,
    );
    console.log("====info=====", info)
  }
})



app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
});
