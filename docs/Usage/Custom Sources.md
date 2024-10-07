<h1 align="center">
  <br>
  <!--<a href=""><img src="" alt="Markdownify" width="200"></a>-->
  <br>
  Custom Sources
  <br>
</h1>

## Overview
You can customise the supported log sources by overwriting the `regex.json` file. You must first create the [formats file](https://github.com/TehMuffinMoo/qsaf/blob/main/Docker/regex.json) within the Docker directory.

This can be exposed through docker volumes as shown in the `compose.yaml` example below.

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
      - ./config.ini:/home/qsaf/config.ini
      - ./regex.json:/home/qsaf/regex.json
      - ./logs:/var/log/syslog-ng
```

## Regex Formats
The `regex.json` file is made up of Regex Categories and Regex strings with Capture Groups for matching.

The following is a <b>snippet</b> from the default [formats file](https://github.com/TehMuffinMoo/qsaf/blob/main/Docker/regex.json) shown as an example.

```json
{
    "Formats": [
        {
            ## This is the name of the Regex Category. The name is referenced when configuring the Syslog Type in the config.ini file
            "Name": "BIND-Query",
            "Regexes": [
                ## The following is a list of Regex Strings to match against. Each String must have the IP-Group, Query-Group, Type-Group & Capture-Groups properties entered correctly.
                {
                    ## This is the Regex string to match logs against during replay. Backslashes must be escaped here.
                    "Regex": ".*client @0x[0-9a-fA-F]+ ([^#]+)#\\d+ \\([^)]+\\): query: ([^ ]+) [A-Za-z]+ ([A-Za-z]+) [+-]+.*$",
                    ## This is the Capture Group where the IP Address is captured, in this case Group 0.
                    "IP-Group": 0,
                    ## This is the Capture Group where the DNS Query is captured, in this case Group 1.
                    "Query-Group": 1,
                    ## This is the Capture Group where the DNS Type is captured, in this case Group 2.
                    "Type-Group": 2,
                    ## This is the number of total capture groups defined in the Regex string. In this case, 3 capture groups have been defined.
                    "Capture-Groups": 3
                }
            ]
        }
    ]
}
```