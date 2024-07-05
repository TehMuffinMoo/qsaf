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

#########################################################	

with open('/var/run/qsaf.pid', 'w', encoding='utf-8') as f:
    f.write(str(os.getpid()))
    
line_number=0
starttime = timeit.default_timer()

config = configparser.ConfigParser()
config.read('/home/qsaf/config.ini')
log_format = config['syslog']['type']
dns_server = config['dns']['forwarder']
view = config['dns']['view']
role = config['server']['role']
print_frequency = int(config['server']['print_frequency'])
debug = config['debug']['enabled']

log_file = '/var/log/syslog-ng/collector.log'
errors = 0
threads = 0

#########################################################

def send_dns_query(qip,qname,qtype,dns_server):
    try:
        TIMEOUT = 0.00000005
        PAYLOAD = 512

        if ':' in qip:
            qip = socket.inet_pton(socket.AF_INET6, qip)
        else:
            qip = socket.inet_aton(qip)

        options = [dns.edns.GenericOption(65523,qip),                        #qip
        #dns.edns.GenericOption(65524,binascii.unhexlify('000000000000')),   #source mac
        dns.edns.GenericOption(65526,view.encode())]            #dns_view

        message = dns.message.make_query(qname, qtype, use_edns=True, options = options)
        if debug=='True':
            print('Payload: \n',message)
            print('########################\n')
        dns.query.udp(message, dns_server, timeout=TIMEOUT)
    except:
        global errors
        errors=+1

    global threads
    threads-=1

def start_job(line):
	qip = qname = qtype = None
	if debug=='True':
		print(line)
	if log_format =='query':
		regex = re.compile(r'.*client @0x[0-9a-fA-F]+ ([^#]+)#\d+ \([^)]+\): query: ([^ ]+) [A-Z]+ ([A-Z]+) [+-]+.*$')
		z = re.match(regex, line)
		if z:
			if len(z.groups()) == 3:
				qip = z.groups()[0]
				qname = z.groups()[1]
				qtype = z.groups()[2]
		else:
			regex2 = re.compile(r'.*client ([^#]+)#\d+ \([^)]+\): view [^:]+: query: ([^ ]+) [A-Z]+ ([^ ]+) ')
			y = re.match(regex2, line)
			if y:
				if len(y.groups()) == 3:
					qip = y.groups()[0]
					qname = y.groups()[1]
					qtype = y.groups()[2]

	if log_format =='response':
		regex = re.compile(r'.*client ([^#]+)#\d+: (UDP|TCP): query: ([^ ]+) [A-Z]+ ([A-Z]+).*$')
		z = re.match(regex, line)
		if z:
			if len(z.groups()) == 4:
				qip = z.groups()[0]
				qname = z.groups()[2]
				qtype = z.groups()[3]
			else:
				regex2 = re.compile(r'.*client ([^#]+)#\d+: query: ([^ ]+) [A-Z]+ ([A-Z]+) .*$')
				y = re.match(regex2, line)
				if y:
					if len(y.groups()) == 3:
						qip = y.groups()[0]
						qname = y.groups()[1]
						qtype = y.groups()[2]
    
	if log_format =='capture':
		regex = re.compile(r'\d+,\d+,Query,,([^,]+),\d+,,I,([^,]+),[^,]+,([^,]+)')
		z = re.match(regex, line)
		if z:
			if len(z.groups()) == 3:
				qip = z.groups()[0]
				qname = z.groups()[1]
				qtype = z.groups()[2]
			
	if not (qip == None and qname == None and qtype == None):
		send_dns_query(qip,qname,qtype,dns_server)
		print("\r", end="")
		print("Queries: ",line_number, "/"," QPS: ",int(line_number/(timeit.default_timer() - starttime)),"Active Threads: ",threads ,"Errors: ",errors, end="")
		if print_frequency != 0:
			if line_number % print_frequency == 0:
				print("\n")
    
def start_threadpool(content):
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        if content is not None:
            for line in content:
                line_number +=1
                line = line.strip()
                threads+=1
                executor.submit(start_job(line))

#########################################################

print('Debug mode is: ',debug)

if role =='forwarder':
    print('Forwarder Mode Enabled. Logs will be collected from /var/log/syslog-ng/logs\r')
    for filename in os.listdir('.'):
        if filename.endswith('.gz'):
            content=gzip.open(filename)
            start_threadpool(content)
        elif filename == 'collector.log':
            content=open(log_file, 'r')
            start_threadpool(content)
elif (role =='both'):
    print('Both Collector & Forwarder Mode enabled.\r')
    content = tailer.follow(open(log_file))
    start_threadpool(content)
elif (role =='collector'):
    content = 'None'
    print('Collector Mode Enabled. Logs will not be forwarded during this session\r')

print("\n")
