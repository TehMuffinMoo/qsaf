<h1 align="center">
  <br>
  <!--<a href=""><img src="" alt="Markdownify" width="200"></a>-->
  <br>
  Detailed Installation Guide
  <br>
</h1>

## Overview
This guide will provide detailed steps for installing Docker & Docker Compose on Ubuntu, and additionally configuring QSAF (Query Store & Forward) as a container.

2. Create a new directory for the Docker files and change into that new directory.
    ```sh
    mkdir /Docker
    cd /Docker
    ```
3. Create a new directory for the log files to be stored in
    ```sh
    mkdir logs
    ```
4. Create & edit the Docker Compose file
    ```sh
    nano compose.yaml
    ```

    <b>Example Docker Compose File</b>
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

5. Create & edit the QSAF Config file
    ```sh
    nano config.ini
    ```

    <b>Example QSAF Configuration File</b>
    You can get the latest example config file from [Github](https://raw.githubusercontent.com/TehMuffinMoo/qsaf/refs/heads/main/config.ini).