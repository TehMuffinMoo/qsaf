<h1 align="center">
  <br>
  <!--<a href=""><img src="" alt="Markdownify" width="200"></a>-->
  <br>
  Collector & Forwarding Mode
  <br>
</h1>

## Overview
The purpose of the 'Both' Mode is to provide a means to perform syslog data collection whilst replaying it immediately for real-time passive data collection.

This applies when `role = both` is set in the `config.ini` file.

### Behaviour
* When performing collection, syslog is received on <b>UDP/514</b> by default (unless changed in Docker Compose configuration).
* The collection is performed by Syslog-NG, with a configured cronjob to rollover logs at 25GB increments. This job is scheduled to run every 30 minutes and keeps a maximum of 10 files.
* Rolled over logs will be compressed into `.gz` format, which commonly reduces the 25GB files to `~1.9GB` in size. This avoids storing unnecessarily large files on disk during collection.
* Files will be located in the logs directory defined within the [Docker Compose](../../Installation/How%20To%20Deploy%20QSAF/#configuring-docker-compose) file
* When in this mode, only new logs received in the `collector.log` file will be replayed as DNS Queries. Rolled over data and events that exist previous to starting the container will not be replayed, as this mode only tails the current log.
    * If you need to replay previously collected DNS queries, use [Forwarding Mode](../Forwarding%20Mode/) instead.
* Forwarding Status / Updates will be posted to the Docker Console / Logs at the interval defined within the [config.ini](../../Installation/How%20To%20Deploy%20QSAF/#config-file) file.
* DNS Queries will be replayed to the Recursive DNS Server specified in the [config.ini](../../Installation/How%20To%20Deploy%20QSAF/#config-file) file.