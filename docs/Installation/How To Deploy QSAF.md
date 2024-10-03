<h1 align="center">
  <br>
  <!--<a href=""><img src="" alt="Markdownify" width="200"></a>-->
  <br>
  How to Deploy QSAF
  <br>
</h1>

## Overview
You can deploy QSAF in an Online (Internet Connected) Environment, or an Offline (No Internet Connectivity) Environment. The steps for both of these options is included in the sections below.

## Pre-Requisites
Ensure you have checked the [list of pre-requisites](../Pre-Requisites).

## Configuring Docker Compose

There is an example configuration included below, which configures the necessary image location, exposed ports, folders & configuration file.

You can customise this example to your needs.

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

## Online Environment
There is no additional steps when using an internet connected environment as the docker container will be downloaded directly from Github Container Repository. You can proceed to creating the <a href="#config-file">config file</a>.

## Deploy QSAF in Offline Environment
When connecting to the Github Docker Repository is not possible from the Docker Server, you can still deploy QSAF with some extra steps included below.

### Import the Tarball
* Download the latest `qsaf.tar` from the <a href="https://github.com/TehMuffinMoo/qsaf/releases" target="_blank">Releases</a> page.

* Transfer the file to the Docker Server

* Import the Docker Container by using `docker load < qsaf.tar`
```bash
sh-3.2$ docker load < qsaf.tar 
63ca1fbb43ae: Loading layer [==================================================>]  3.624MB/3.624MB
f0d007d7e628: Loading layer [==================================================>]  22.14MB/22.14MB
bfa943ef6db4: Loading layer [==================================================>]  6.301MB/6.301MB
31bacb415970: Loading layer [==================================================>]  6.215MB/6.215MB
47824014ab7c: Loading layer [==================================================>]     141B/141B
d337dc9ff2f7: Loading layer [==================================================>]     427B/427B
546f4abf15a4: Loading layer [==================================================>]  173.3kB/173.3kB
3accd1cc51af: Loading layer [==================================================>]     293B/293B
0120830fd7e7: Loading layer [==================================================>]     115B/115B
c11811a6bdca: Loading layer [==================================================>]     251B/251B
209ee5186e39: Loading layer [==================================================>]  2.304kB/2.304kB
e6803d34a201: Loading layer [==================================================>]     201B/201B
c1f998bc5540: Loading layer [==================================================>]     235B/235B
8cbda5a14e4a: Loading layer [==================================================>]     246B/246B
c41d2892bc8c: Loading layer [==================================================>]  2.299kB/2.299kB
Loaded image: ghcr.io/tehmuffinmoo/qsaf:latest
```

* Verify the Docker Image has been loaded by using `docker image ls`
```bash
sh-3.2$ docker image ls
REPOSITORY                           TAG       IMAGE ID       CREATED             SIZE
ghcr.io/tehmuffinmoo/qsaf            latest    0de3acf76154   About an hour ago   99.4MB
```

### Config File
Create the config file, ensuring it aligns with the one specified in [Configuring Docker Compose](#configuring-docker-compose).

You can get the latest example config file from [Github](https://github.com/TehMuffinMoo/qsaf/blob/main/config.ini).

Each of the options within the Config File are detailed below.

| Section | Option | Value(s) | Description |
|---------|--------|----------|-------------|
| server  | role | `collector`, `forwarder`, `both` | Specify the mode to run QSAF in. The Modes are described in more detail [here](#Placeholder). |
| server  | print_frequency | int | The frequency in which updates are printed to the docker log. Setting to 0 will turn off updates. |
| dns     | type | `Plain`, `DoH`, `DoT` | The type of DNS Query to use when replaying data. Plain is via UDP. DNS over HTTPS & DNS over TLS will have considerable performance impact. |
| dns     | forwarder | ip | The IP Address of the Recursive DNS Server to use when replaying data. |
| dns     | view | string | The name of the DNS View to use when replaying data into Infoblox Portal. |
| dns     | ignored_domains | csv | A comma separated string of domains to exclude when replaying log data. |
| syslog  | type | `query`, `response`, `capture` | The Syslog Type indicates the source data type when regex matching in forwarding mode. |
| debug   | enabled | `true`, `false` | Enabling Debug Mode will print every query to console. |

### Start Docker Compose
Once everything is configured, you can proceed to start the container using `docker compose up`