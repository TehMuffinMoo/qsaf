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

#########################################################	

with open('/var/run/qsaf.pid', 'w', encoding='utf-8') as f:
    f.write(str(os.getpid()))
    
line_number=0
starttime = timeit.default_timer()

config = configparser.ConfigParser()
config.read('/home/qsaf/config.ini')
log_format = config['syslog']['type']
dns_server = config['dns']['forwarder']
dns_server_type = config['dns']['type']
view = config['dns']['view']
role = config['server']['role']
print_frequency = int(config['server']['print_frequency'])
debug = config['debug']['enabled']
if config['dns']['ignored_domains'] == '':
    ignored_domains = None
else:
    ignored_domains = config['dns']['ignored_domains'].split(',')

log_file = '/var/log/syslog-ng/collector.log'
queries = 0 # Number of queries processed
errors = 0  # Number of errors encountered
threads = 0 # Number of active threads
ignored = 0 # Number of queries ignored through the use of 'ignored_domains'
skipped = 0 # Number of log lines skipped due to non-conforming regex. (Usually just noise in the logs)

#########################################################

def send_dns_query(qip,qname,qtype,dns_server,type):
    global errors
    try:
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
        try:
            match type:
                case 'Plain':
                    #dns.query.udp(message, dns_server, timeout=0.00000005)
                    dns.query.udp(message, dns_server, timeout=0.00000005)
                case 'DoH':
                    #dns.query.https(message, dns_server, timeout=1)
                    dns.query.https(message, 'https://'+dns_server+'/dns-query', timeout=1)
                case 'DoT':
                    #dns.query.tls(message, dns_server, timeout=1)
                    dns.query.tls(message, dns_server, timeout=1)
                case _:
                    print('Invalid DNS Server Type')
        except:
            if type!='Plain':
                errors+=1
    except:
        errors+=1

    global threads
    threads-=1

def start_job(line):
	global threads
	global queries
	global ignored
	global skipped
	qip = qname = qtype = None
	if debug=='True':
		print(line)
	if log_format =='query':
		regex = re.compile(r'.*client @0x[0-9a-fA-F]+ ([^#]+)#\d+ \([^)]+\): ((view [^:]+): )?query: ([^ ]+) [A-Za-z]+ ([A-Za-z]+) [+-]+.*$')
		z = re.match(regex, line)
		if z:
			if len(z.groups()) == 3:
				qip = z.groups()[0]
				qname = z.groups()[1]
				qtype = z.groups()[2]
		else:
			regex2 = re.compile(r'.*client ([^#]+)#\d+ \([^)]+\): view [^:]+: query: ([^ ]+) [A-Za-z]+ ([^ ]+) ')
			y = re.match(regex2, line)
			if y:
				if len(y.groups()) == 3:
					qip = y.groups()[0]
					qname = y.groups()[1]
					qtype = y.groups()[2]

	elif log_format =='response':
		regex = re.compile(r'.*client ([^#]+)#\d+: (UDP|TCP): query: ([^ ]+) [A-Za-z]+ ([A-Za-z]+).*$')
		z = re.match(regex, line)
		if z:
			if len(z.groups()) == 4:
				qip = z.groups()[0]
				qname = z.groups()[2]
				qtype = z.groups()[3]
			else:
				regex2 = re.compile(r'.*client ([^#]+)#\d+: query: ([^ ]+) [A-Za-z]+ ([A-Za-z]+) .*$')
				y = re.match(regex2, line)
				if y:
					if len(y.groups()) == 3:
						qip = y.groups()[0]
						qname = y.groups()[1]
						qtype = y.groups()[2]
    
	elif log_format =='capture':
		regex = re.compile(r'\d+,\d+,Query,,([^,]+),\d+,,I,([^,]+),[^,]+,([^,]+)')
		z = re.match(regex, line)
		if z:
			if len(z.groups()) == 3:
				qip = z.groups()[0]
				qname = z.groups()[1]
				qtype = z.groups()[2]
			
	if not (qip == None and qname == None and qtype == None):
		ignore = False
        ## Skip ignored domains
		if ignored_domains is not None:
			for igdom in ignored_domains:
				if ignore == False:
					if igdom in qname:
						ignore = True
		if ignore == False:
			queries +=1
			send_dns_query(qip,qname,qtype,dns_server,dns_server_type)
		else:
			ignored+=1
			threads-=1
		print("\r", end="")
		print("Queries:",queries, " / ","QPS:",int(queries/(timeit.default_timer() - starttime))," (Processed:",line_number," Active Threads:",threads," Errors:",errors," Ignored:",ignored," Skipped:",skipped, end=")")
		if print_frequency != 0:
			if queries % print_frequency == 0:
				print("\n")
	else:
		threads-=1
		skipped+=1
    
def start_threadpool(content):                                              
    global threads
    global line_number
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        if content is not None:                         
            for line in content:                    
                if isinstance(line, (bytes, bytearray)):
                    line = str(line, "utf-8").strip()
                else:                           
                    line = line.strip()                  
                threads+=1
                line_number+=1
                executor.submit(start_job(line))

#########################################################

print('Debug mode is: ',debug)

if role =='forwarder':
    print('Forwarder Mode Enabled. Logs will be collected from /var/log/syslog-ng/logs\r')
    lst = sorted(os.listdir('/var/log/syslog-ng/'), reverse=True)
    for filename in lst:
        filepath = '/var/log/syslog-ng/'+filename
        if filename.endswith('.gz'):
            content=gzip.open(filepath)
            print("\n")
            print('Processing:',filename)
            print("\n")
            start_threadpool(content)
        elif filename == 'collector.log' or filename.endswith('.txt'):
            print("\n")
            print('Processing:',filepath)
            print("\n")
            content=open(filepath, 'r')
            start_threadpool(content)
    print('\nLog forwarding complete.')
elif (role =='both'):
    print('Both Collector & Forwarder Mode enabled.\r')
    content = tailer.follow(open(log_file))
    start_threadpool(content)
elif (role =='collector'):
    content = 'None'
    print('Collector Mode Enabled. Logs will not be forwarded during this session\r')

print("\n")
