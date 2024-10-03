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

## Logging
When replaying the logs in either 'both' or 'forwarder' mode, you will see log entries in the docker logs as follows;

`Queries: 2207821  /  QPS: 2983  (Processed: 2321734  Active Threads: 0  Errors: 0  Ignored: 112554  Skipped: 1359)`

These metrics are descibed as follows;

| Metric         | Description |
-----------------|--------------
| Queries        | The number of processed / forwarded DNS Queries |
| QPS            | The calculated queries per second when replaying logs |
| Processed      | The total number of log lines processed (Should be equal to the sum of Queries, Ignored & Skipped) |
| Active Threads | The number of active threads |
| Errors         | The number of errors encountered when processing |
| Ignored        | The number of queries ignored through the use of the 'ignored_domains' configuration option |
| Skipped        | The number of log lines skipped due to non-conforming regex. (Usually just random syslog noise in the logs) |