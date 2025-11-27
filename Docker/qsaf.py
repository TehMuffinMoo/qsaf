#!/usr/bin/python3
import logging
import struct
import re
import socket
import binascii
import dns
import dns.resolver
import dns.message
import dns.query
import dns.edns
import dns.flags
import concurrent.futures
import timeit
import tailer
import os
import configparser
import gzip
import httpx
import json
import pandas as pd
import pyarrow.parquet as pq
import sys
import time

#########################################################
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

with open('/var/run/qsaf.pid', 'w', encoding='utf-8') as f:
    f.write(str(os.getpid()))

line_number = 0
starttime = timeit.default_timer()

config = configparser.ConfigParser()
config.read('/home/qsaf/config.ini')
dns_server = config['dns']['forwarder']
dns_server_type = config['dns']['type']

# Validate Syslog Type
log_format = config['syslog']['type']
with open("/home/qsaf/regex.json", encoding="utf8") as regexfile:
    data = json.load(regexfile)
    regexconfig = [x for x in data['Formats'] if x['Name'] == log_format]
    if len(regexconfig) < 1:
        logging.error(f"Unable to find regex defined with name: {log_format}")
        raise SystemExit
    elif len(regexconfig) > 1:
        logging.error(f"More than one regex configuration returned for name: {log_format}")
        raise SystemExit

view = config['dns']['view']
role = config['server']['role']
print_frequency = int(config['server']['print_frequency'])
debug = config['debug']['enabled']
ignored_domains = config['dns']['ignored_domains'].split(',') if config['dns']['ignored_domains'] else None

log_file = '/var/log/syslog-ng/collector.log'
queries = errors = threads = ignored = skipped = 0

#########################################################

def send_dns_query(qip, qname, qtype, dns_server, type):
    global errors, threads
    try:
        if ':' in qip:
            qip = socket.inet_pton(socket.AF_INET6, qip)
        else:
            qip = socket.inet_aton(qip)

        options = [
            dns.edns.GenericOption(65523, qip),
            dns.edns.GenericOption(65526, view.encode())
        ]

        message = dns.message.make_query(qname, qtype, use_edns=True, options=options)
        if debug == 'True':
            logging.debug(f"Payload:\n{message}\n########################\n")

        try:
            match type:
                case 'Plain':
                    dns.query.udp(message, dns_server, timeout=0.00000005)
                case 'DoH':
                    dns.query.https(message, f'https://{dns_server}/dns-query', timeout=1)
                case 'DoT':
                    dns.query.tls(message, dns_server, timeout=1)
                case _:
                    logging.error('Invalid DNS Server Type')
        except:
            if type != 'Plain':
                errors += 1
    except:
        errors += 1
    threads -= 1

def start_job(line):
    global threads, queries, ignored, skipped
    qip = qname = qtype = None
    if debug == 'True':
        logging.debug(line)
    if regexconfig:
        for regex in regexconfig[0]['Regexes']:
            z = re.match(regex['Regex'], line)
            if z and len(z.groups()) == regex['Capture-Groups']:
                qip = z.groups()[regex['IP-Group']]
                qname = z.groups()[regex['Query-Group']]
                qtype = z.groups()[regex['Type-Group']]
                break

    if qip and qname and qtype:
        ignore = False
        if ignored_domains:
            for igdom in ignored_domains:
                if igdom in qname:
                    ignore = True
                    break
        if not ignore:
            queries += 1
            send_dns_query(qip, qname, qtype, dns_server, dns_server_type)
        else:
            ignored += 1
            threads -= 1
        if print_frequency and queries % print_frequency == 0:
            logging.info(f"Queries: {queries} / QPS: {int(queries/(timeit.default_timer() - starttime))} "
                         f"(Processed: {line_number} Active Threads: {threads} Errors: {errors} Ignored: {ignored} Skipped: {skipped})")
    else:
        threads -= 1
        skipped += 1


def start_job_direct(qip, qname, qtype):
    global threads, queries, ignored, skipped
    ignore = False
    if ignored_domains:
        for igdom in ignored_domains:
            if igdom in qname:
                ignore = True
                break
    if not ignore:
        queries += 1
        send_dns_query(qip, qname, qtype, dns_server, dns_server_type)
    else:
        ignored += 1
        threads -= 1
    if print_frequency and queries % print_frequency == 0:
        logging.info(f"Queries: {queries} / QPS: {int(queries/(timeit.default_timer() - starttime))} "
                     f"(Processed: {line_number} Active Threads: {threads} Errors: {errors} Ignored: {ignored} Skipped: {skipped})")


def start_threadpool(content, executor):
    global threads, line_number
    if content:
        for line in content:
            if isinstance(line, (bytes, bytearray)):
                line = str(line, "utf-8").strip()
            else:
                line = line.strip()
            threads += 1
            line_number += 1
            executor.submit(start_job, line)

#########################################################

logging.info(f"Debug mode is: {debug}")

executor = concurrent.futures.ThreadPoolExecutor(max_workers=50)

if role == 'forwarder':
    logging.info('Forwarder Mode Enabled. Logs will be collected from /var/log/syslog-ng/logs')
    lst = sorted(os.listdir('/var/log/syslog-ng/'), reverse=True)
    for filename in lst:
        filepath = f'/var/log/syslog-ng/{filename}'
        if filename.endswith('.gz'):
            logging.info(f"Processing: {filename}")
            content = gzip.open(filepath)
            start_threadpool(content, executor)
        elif filename == 'collector.log' or filename.endswith('.txt'):
            logging.info(f"Processing: {filepath}")
            content = open(filepath, 'r')
            start_threadpool(content, executor)
        elif filename.endswith('.parquet'):
            logging.info(f"Processing Parquet file: {filepath}")
            parquet_file = pq.ParquetFile(filepath)
            for batch in parquet_file.iter_batches(columns=['qip', 'qname', 'qtype'], batch_size=10000):
                df = batch.to_pandas()
                for row in df.itertuples(index=False):
                    threads += 1
                    line_number += 1
                    while threads > 1_000_000:
                        logging.warning(f"Queue limit reached: {threads} tasks queued. Waiting 60s for backlog to clear...")
                        time.sleep(60)  # Sleep for 60 second before checking again
                    executor.submit(start_job_direct, row.qip, row.qname, row.qtype)

elif role == 'both':
    logging.info('Both Collector & Forwarder Mode enabled.')
    content = tailer.follow(open(log_file))
    start_threadpool(content, executor)

elif role == 'collector':
    logging.info('Collector Mode Enabled. Logs will not be forwarded during this session')

executor.shutdown(wait=True)
logging.info("Processing complete.")
