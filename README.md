## Docker Compose Example
```
version: '3'

services:
  qsaf:
    image: ghcr.io/tehmuffinmoo/qsaf:latest
    ports:
      - 514:514/udp
    environment:
      HWID: RANDOM
      LOGLEVEL: INFO
    restart: always
    volumes:
      - ./config.ini:/home/qsaf/config.ini
      - ./logs:/var/log/syslog-ng
```
