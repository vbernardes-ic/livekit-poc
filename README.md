# Livekit POC using Egress for track recording

## Using docker-compose:

`$ docker compose up`

## Installing manually:

### Install Livekit
`$ brew install livekit`

### Run Livekit
`$ livekit-server --config /path/to/project/livekit-server-config.yaml --dev`

### Install redis
`$ brew install redis`

### Configure redis

See https://docs.livekit.io/oss/deployment/egress/#running-locally

_redis.conf file may be at /opt/homebrew/etc/ instead of /usr/local/etc/_

### Run Egress
```
docker run --rm \
    -e EGRESS_CONFIG_FILE=/out/config.yaml \
    -v /path/to/project/livekit-egress:/out \
    livekit/egress`
```

## Install frontend and backend

Inside example and backend folder, run `$ yarn/npm install`

## Run frontend and backend (on each respective folder)

`$ yarn/npm start`

## Run websocket server (on backend folder)

`$ yarn/npm start-wss`