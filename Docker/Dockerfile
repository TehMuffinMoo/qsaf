FROM alpine:latest

## Install Python
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 py3-pip && ln -sf python3 /usr/bin/python
RUN pip install dnspython[doh] tailer --break-system-packages

## Install Syslog-NG
RUN apk add --update --no-cache syslog-ng
RUN mkdir /var/log/syslog-ng
ADD ./Docker/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf

## Install Logrotate
RUN apk add --update --no-cache logrotate
ADD ./Docker/logrotate.conf /etc/logrotate.d/syslog-ng

## Make base directory
RUN mkdir /home/qsaf

## Add Scripts
ADD ./Docker/startup /home/qsaf/startup
ADD ./Docker/qsaf.py /home/qsaf/qsaf.py
ADD ./Docker/logrotate.cron /etc/qsaf/syslog-ng.cron
RUN crontab /etc/qsaf/syslog-ng.cron

## Set permissions
RUN chmod +x /home/qsaf/startup
RUN chmod +x /home/qsaf/qsaf.py

## Set Python Output
ENV PYTHONUNBUFFERED=1

## Add entrypoint
ENTRYPOINT ["/bin/sh","/home/qsaf/startup"]
