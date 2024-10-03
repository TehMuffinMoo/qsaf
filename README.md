<h1 align="center">
  <br>
  <!--<a href=""><img src="" alt="Markdownify" width="200"></a>-->
  <br>
  Query Store & Forward (QSAF)
  <br>
</h1>

<p align="center">
  <a href="https://github.com/TehMuffinMoo/qsaf"><img src="https://img.shields.io/github/v/release/TehMuffinMoo/qsaf.svg?label=Github Release"></a>
  <a href="https://github.com/TehMuffinMoo/qsaf"><img src="https://img.shields.io/github/languages/code-size/TehMuffinMoo/qsaf.svg?label=Code%20Size"></a>
  <a href="https://raw.githubusercontent.com/TehMuffinMoo/qsaf/main/LICENSE"><img src="https://img.shields.io/github/license/TehMuffinMoo/qsaf?label=License"></a>
  <a href="https://github.com/TehMuffinMoo/qsaf/releases"><img src="https://img.shields.io/github/release-date/tehmuffinmoo/qsaf?label=Latest%20Release"></a>
  <a href="https://qsaf.readthedocs.io"><img src="https://img.shields.io/readthedocs/qsaf?label=Docs"></a>
  <a href="https://www.codefactor.io/repository/github/tehmuffinmoo/qsaf"><img src="https://www.codefactor.io/repository/github/tehmuffinmoo/qsaf/badge"></a>
</p>

<h4 align="center">A Docker Container used to Store & Forward DNS Queries.</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="https://qsaf.readthedocs.io" target="_blank">Documentation</a> •
  <a href="#key-features">Feature Requests</a> •
  <a href="#license">License</a> •
</p>

## Key Features

* Collect DNS Syslog data in various formats
* Replay the collected log data as DNS Queries either in real time or separately later on
* Replayed data retains original source IP and that is subsequently injected into the EDNS Headers of the DNS Queries

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

## Feature Requests

* If the feature you are looking for is not yet built into the QSAF Container, you can raise a feature request via [Github Issues](https://github.com/TehMuffinMoo/qsaf/issues).

## License

MIT

---

> [Mat Cox]()
