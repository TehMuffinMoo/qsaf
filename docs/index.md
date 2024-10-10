
<style>
  .paramName {
    white-space: nowrap;
  }
</style>

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
  <a href="#overview">Overview</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#key-features">Feature Requests</a> •
  <a href="https://github.com/TehMuffinMoo/qsaf" target="_blank">Github</a> •
  <a href="#license">License</a>
</p>

## Overview
QSAF was designed to provide a means of passive DNS log collection for the purpose of an Infoblox Security Assessment.

You can collect DNS Syslog data in various formats, which can then be replayed as DNS queries in real time or stored for replaying at a later time.

Collected data will retain the original Source IP during replayed queries when sending them to the Infoblox Threat Defense Cloud Resolvers.

## Feature Requests

* If the feature you are looking for is not yet built into the QSAF Container, you can raise a feature request via [Github Issues](https://github.com/TehMuffinMoo/qsaf/issues).

## License

MIT

---

> [Mat Cox]()
