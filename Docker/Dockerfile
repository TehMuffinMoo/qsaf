FROM alpine:latest

## Install Python
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 py3-pip && ln -sf python3 /usr/bin/python
RUN pip install dnspython tailer --break-system-packages

## Install Syslog-NG
RUN apk add --update --no-cache syslog-ng
RUN mkdir /var/log/syslog-ng
ADD ./Docker/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf

## Install Logrotate
RUN apk add --update --no-cache logrotate

## Make base directory
RUN mkdir /home/qsaf

## Add Scripts
ADD ./Docker/startup /home/qsaf/startup
ADD ./Docker/qsaf.py /home/qsaf/qsaf.py
ADD ./Docker/logrotate.cron /etc/crontabs/syslog-ng

## Set permissions
RUN chmod +x /home/qsaf/startup
RUN chmod +x /home/qsaf/qsaf.py

## Add entrypoint
ENTRYPOINT ["/bin/sh","/home/qsaf/startup"]
