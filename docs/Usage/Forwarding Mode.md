<h1 align="center">
  <br>
  <!--<a href=""><img src="" alt="Markdownify" width="200"></a>-->
  <br>
  Forwarding Mode
  <br>
</h1>

## Overview
The purpose of the 'Forwarder' Mode is to provide a means to replay previously collected data, retaining the original Source IP.

This applies when `role = forwarder` is set in the `config.ini` file.

### Behaviour
* When performing forwarding, QSAF will collect any files ending in `.txt`, `.gz` and named `collector.log`.
* Files to process must be located in the logs directory defined within the [Docker Compose](.../Installation/How%20To%20Deploy%20QSAF/#configuring-docker-compose) file
* Files will be processed in reverse order, with the aim to replay the data in the same order in which it was originally received.
* Forwarding Status / Updates will be posted to the Docker Console / Logs at the interval defined within the [config.ini](.../Installation/How%20To%20Deploy%20QSAF/#config-file) file
* Once all logs are processed, the forwarding will stop automatically.
* Forwarding mode does not prevent collection of additional data, as Syslog-NG is still operating in the background.
    * It is suggested you turn off Syslog Feeds to QSAF prior to enabling forwarding mode, as logs received after the container is started will not be forwarded.
    * If you need to send DNS queries in real-time of when they are received, use [Collector & Forwarding Mode](../Collector%20%26%20Forwarding%20Mode/) instead.