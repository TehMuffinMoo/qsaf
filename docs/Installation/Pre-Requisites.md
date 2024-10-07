<h1 align="center">
  <br>
  <!--<a href=""><img src="" alt="Markdownify" width="200"></a>-->
  <br>
  Pre-Requisites
  <br>
</h1>

## Pre-Requisites
The list of pre-requisites to use QSAF is included below;

* You must have Docker & Docker Compose installed (Any supported OS is fine). See installation instructions [here](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository).
* You must have access to download the Docker Container from `ghcr.io`. This could be direct from the machine with Docker installed, or via manually downloading and transferring the tarball.
* If using QSAF in `Collector` or `Both` mode, the DNS Server(s) must have access to send syslog (default is UDP/514) to the QSAF instance
* If using QSAF in `Forwarder` or `Both` mode, the QSAF instance must have access to send DNS queries to the forwarder defined in the `config.ini` file.