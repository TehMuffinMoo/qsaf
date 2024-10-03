<h1 align="center">
  <br>
  <!--<a href=""><img src="" alt="Markdownify" width="200"></a>-->
  <br>
  Collector Mode
  <br>
</h1>

## Overview
The purpose of 'Collector' Mode is to provide a means to perform syslog data collection, for replaying at a later time.

This applies when `role = collector` is set in the `config.ini` file.

### Behaviour
* When performing collection, syslog is received on <b>UDP/514</b> by default (unless changed in Docker Compose configuration).
* The collection is performed by Syslog-NG, with a configured cronjob to rollover logs at 25GB increments. This job is scheduled to run every 30 minutes and keeps a maximum of 10 files.
* Rolled over logs will be compressed into `.gz` format, which commonly reduces the 25GB files to `~1.9GB` in size. This makes the files easily transferrable and avoids storing unnecessarily large files on disk during collection.
* Compressed `.gz` logs can later be replayed without the need for decompression, thus saving necessary space requirements on the machine doing the forwarding.
* The Docker Console is expected to be blank during this time, except the messages when the container is started.