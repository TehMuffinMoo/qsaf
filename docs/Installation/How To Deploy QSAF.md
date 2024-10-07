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

## Configuring Docker / Compose
!!! warning "Important Note"

    Creating a directory under root assumes root privileges, either directly or through the use of sudo.

1. Create a new directory for the Docker files and change into that new directory.
    ```sh
    mkdir /Docker
    cd /Docker
    ```
2. Create a new directory for the log files to be stored in
    ```sh
    mkdir /Docker/logs
    ```
3. Create & edit the Docker Compose file
    ```sh
    nano /Docker/compose.yaml
    ```

    <b>Example Docker Compose File</b>

    There is an example configuration included below, which configures the necessary image location, exposed ports, folders & configuration file.

    You can customise this example to your needs.

    ```yaml
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
          - /Docker/config.ini:/home/qsaf/config.ini
          - /Docker/logs:/var/log/syslog-ng
    ```
4. Create & edit the QSAF Config file
    ```sh
    nano config.ini
    ```

    <b>Example QSAF Configuration File</b>

    ??? info "config.ini"

        ```ini
        [server]
        ## The role of the qsaf container.
        #### collector will simply collect syslog data via syslog-ng and keep it for future use
        #### forwarder will take existing syslog-ng data and generate queries to the DNS forwarder
        #### both will collect syslog data and generate queries in real time
        role = both
        ## The frequency in which updates are printed to the docker log. Setting to 0 will turn off updates.
        print_frequency = 100

        [dns]
        ## The DNS Server Type to use when forwarding requests. (Plain/DoH/DoT)
        type = Plain
        ## The DNS Server to forward requests to
        forwarder = 52.119.40.100
        ## The DNS View name to apply to forwarded requests
        view = mcox-sa
        ## A comma-separated list of domains to ignore when replaying queries. This is useful for excluding internal domains. Leave blank to send all queries.
        ignored_domains = mydomain.corp,intranet.acme.lab

        [syslog]
        ## The type of syslog to use for regex matching.
        ## BIND-Query    # The Query log format for BIND / Infoblox NIOS
        ## BIND-Response # The Response log format for BIND / Infoblox NIOS
        ## NIOS-Capture  # The Infoblox NIOS Capture log format
        ## Unbound-Query # The Unbound DNS Query log format
        type = BIND-Query

        [debug]
        ## Debug logging (True/False)
        enabled = False
        ```
    
    See the [Config File](#config-file) section for details on QSAF configuration.

### Config File
When creating the config file, ensure it aligns with the one specified in [Configuring Docker Compose](#:~:text=%2D%20/Docker/config.ini%3A/home/qsaf/config.ini).

You can get the latest example config file from [Github](https://github.com/TehMuffinMoo/qsaf/blob/main/config.ini).

Each of the options within the Config File are detailed below.

| Section | Option | Value(s) | Description |
|---------|--------|----------|-------------|
| server  | role | `collector`, `forwarder`, `both` | Specify the mode to run QSAF in. The Modes are described in more detail here: [Collector](../../Usage/Collector%20Mode/)  [Forwarder](../../Usage/Forwarding%20Mode/)  [Both](../../Usage/Collector%20%26%20Forwarding%20Mode/). |
| server  | print_frequency | int | The frequency in which updates are printed to the docker log. Setting to 0 will turn off updates. |
| dns     | type | `Plain`, `DoH`, `DoT` | The type of DNS Query to use when replaying data. Plain is via UDP. DNS over HTTPS & DNS over TLS will have considerable performance impact. |
| dns     | forwarder | ip | The IP Address of the Recursive DNS Server to use when replaying data. |
| dns     | view | string | The name of the DNS View to use when replaying data into Infoblox Portal. |
| dns     | ignored_domains | csv | A comma separated string of domains to exclude when replaying log data. |
| syslog  | type | `BIND-Query`, `BIND-Response`, `NIOS-Capture`, `Unbound-Query` | The Syslog Type indicates the source data type when regex matching in forwarding mode. |
| debug   | enabled | `true`, `false` | Enabling Debug Mode will print every query to console. |

## Online Environment
There is no additional steps when using an internet connected environment as the docker container will be downloaded directly from Github Container Repository.

## Deploy QSAF in Offline Environment
When connecting to the Github Docker Repository is not possible from the Docker Server, you can still deploy QSAF with some extra steps included below.

### Installing from Source
1. Download the latest `qsaf.tar` from the <a href="https://github.com/TehMuffinMoo/qsaf/releases" target="_blank">Releases</a> page.

2. Transfer the tar file to the Docker Server via SCP/FTP/etc.

3. Import the Docker Container Image by using `docker load < qsaf.tar`
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

### Start/Stop Docker Compose
Once everything is configured, you can proceed to start the container using `docker compose up` or `docker compose up -d` to start it in daemon mode (in the background).

!!! warning "Important Note"

    The QSAF Docker Instance must have Read/Write access to the docker directory. If this was created/owned by root, you must also start the container using root/sudo.

!!! info "Note"

    When starting the container with Docker Compose, your current directory must be the docker directory where the `compose.yaml` file is located.

If using daemon mode, you can check the logs as described [here](../../Usage/Log%20Output/).

Once you have finished collecting and/or forwarding DNS Queries, you can stop the QSAF container by running `docker compose down`.