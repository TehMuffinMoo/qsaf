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

#########################################################	

with open('/var/run/replay-query-log.pid', 'w', encoding='utf-8') as f:
    f.write(str(os.getpid()))

config = configparser.ConfigParser()
#config.read('/docker/qsaf/config.ini')
config.read('/home/qsaf/config.ini')
log_format = config['queryformat']['source']
dns_server = config['dnsforwarder']['forwarder']
role = config['role']['role']
debug = config['debug']['state']

print('Debug mode is: '+debug+'\r',end="")

#logging.basicConfig(handlers = [logging.FileHandler('replay-query.log'), logging.StreamHandler()],level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#log_file = 'dns-query.log'
log_file = '/var/log/syslog-ng/logs'
#log_format = 'query' #query, response, capture
#dns_server = '52.119.40.100'
#dns_server = '8.8.8.8'
errors = 0
threads = 0

#########################################################

def send_dns_query(qip,qname,qtype,dns_server):
    try:
        TIMEOUT = 0.05
        PAYLOAD = 512

        if ':' in qip:
            qip = socket.inet_pton(socket.AF_INET6, qip)
        else:
            qip = socket.inet_aton(qip)

        options = [dns.edns.GenericOption(65523,qip),                        #qip
        #dns.edns.GenericOption(65524,binascii.unhexlify('000000000000')),   #source mac
        dns.edns.GenericOption(65526,'POC'.encode())]            #dns_view

        message = dns.message.make_query(qname, qtype, use_edns=True, options = options)
        #message.payload = PAYLOAD
        if debug=='True':
            print(message+'\r',end="")

        dns.query.udp(message, dns_server, timeout=TIMEOUT)
    except:
        global errors
        errors=+1

    global threads
    threads-=1

#########################################################

if role =='forwarder':
    print('Forwarder Mode Enabled. Logs will be collected from /var/log/syslog-ng/logs\r')
    file=open(log_file, 'r')
    content = file.readlines()
elif (role =='both'):
    print('Both Collector & Forwarder Mode enabled.\r')
    content = tailer.follow(open(log_file))
elif (role =='collector'):
    content = 'None'
    print('Collector Mode Enabled. Logs will not be forwarded during this session\r')

line_number=0
starttime = timeit.default_timer()

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:

	if content is not None:
		for line in content:
			line_number +=1
			line = line.strip()
			qip = qname = qtype = None
			if debug=='True':
				print(line)
			if log_format =='query':
				regex = re.compile(r'.*client @0x[0-9a-fA-F]+ ([^#]+)#\d+ \([^)]+\): query: ([^ ]+) [A-Z]+ ([A-Z]+) [+-]+.*$')
				z = re.match(regex, line)
				if z:
					#print (len(z.groups()))
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
				#print (z)
				if z:
					if len(z.groups()) == 4:
						#logging.debug((z.groups()))
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
						#logging.debug((z.groups()))
						qip = z.groups()[0]
						qname = z.groups()[1]
						qtype = z.groups()[2]

			print("")
			if not (qip == None and qname == None and qtype == None):
				executor.submit(send_dns_query(qip,qname,qtype,dns_server))
				threads+=1
				print("\r", end="")
				print("Queries: ",line_number, "/"," QPS: ",int(line_number/(timeit.default_timer() - starttime)),"Active Threads: ",threads ,"Errors: ",errors, end="")
   
print("\n")
