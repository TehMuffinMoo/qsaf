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

#########################################################	

with open('/var/run/qsaf.pid', 'w', encoding='utf-8') as f:
    f.write(str(os.getpid()))
    
line_number=0
starttime = timeit.default_timer()

config = configparser.ConfigParser()
config.read('/home/qsaf/config.ini')
log_format = config['syslog']['type']
dns_server = config['dns']['forwarder']

## Check valid Syslog Type has been set
dns_server_type = config['dns']['type']
with open("/home/qsaf/regex.json", encoding="utf8") as regexfile:
    data = json.load(regexfile)
    regexconfig = [x for x in data['Formats'] if x['Name'] == dns_server_type]
    if len(regexconfig) < 1:
        print('Error! Unable to find any regex defined with name:',dns_server_type)
        raise SystemExit
    elif len(regexconfig) > 1:
        print('Error! More than one regex configuration was returned with name:',dns_server_type)
        raise SystemExit
        
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
	if regexconfig:
		for regex in regexconfig[0]['Regexes']:
			z = re.match(regex['Regex'], line)
			if z:
				if len(z.groups()) == regex['Capture-Groups']:
					qip = z.groups()[regex['IP-Group']]
					qname = z.groups()[regex['Query-Group']]
					qtype = z.groups()[regex['Type-Group']]
					break
			
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
