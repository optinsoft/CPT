#!/usr/bin/env python

# Copyright (c) 2022 Vitaly Yakovlev <vitaly@optinsoft.net>
#
# This script allows to forward multiple local ports to the remote host:port via SSH.
# If argument "count" equals 1 then it works exactly as this command:
#
#   ssh -L local_port:remote_ip:remote_port ssh_user@ssh_host -i ssh_keyfile
#
# If count = 2 then it is similar to run 2 parallel commands:
#
#   ssh -L local_port:remote_ip:remote_port ssh_user@ssh_host -i ssh_keyfile
#   ssh -L (local_port+1):(remote_ip+1):remote_port ssh_user@ssh_host -i ssh_keyfile
#
# etc.

import paramiko, sys
from forward import ForwardServer, Handler
import threading
import sys
from termcolor import colored
import argparse
import ipaddress

def forward_tunnel_server(local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHander(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
    return ForwardServer(("", local_port), SubHander)

parser = argparse.ArgumentParser(description="Cloud phones manager")

parser.add_argument('--local-port', required=True, type=int, help='local (client) port is to be forwarded to the REMOTE_IP:REMOTE_PORT')
parser.add_argument('--remote-ip', required=True, help='remote host IP')
parser.add_argument('--remote-port', required=True, type=int, help='remote host port')
parser.add_argument('--count', default=1, type=int, help='count of the forwarded ports; first local port will be forwarded to the REMOTE_IP:REMOTE_PORT, second - to the REMOTE_IP+1:REMOTE_PORT, etc.')
parser.add_argument('--ssh-host', required=True, help='SSH host')
parser.add_argument('--ssh-port', default=22, type=int, help='SSH port')
parser.add_argument('--ssh-user', required=True, help='SSH user')
parser.add_argument('--ssh-keyfile', required=True, help='SSH private key file')

args = parser.parse_args()

remote_ip = ipaddress.ip_address(args.remote_ip)
count = args.count
remote_port = args.remote_port
local_port = args.local_port

ssh_host = args.ssh_host
ssh_port = args.ssh_port
ssh_user = args.ssh_user
ssh_keyfile = args.ssh_keyfile

ssh_key = paramiko.RSAKey.from_private_key_file(ssh_keyfile)

transport = paramiko.Transport((ssh_host, ssh_port))

transport.connect(hostkey  = None,
                  username = ssh_user,
                  pkey     = ssh_key)

forward_servers = []
forwarding_threads = []

try:
    for i in range(0, count):        
        remote_host = str(remote_ip + i)
        forward_servers.append(forward_tunnel_server(local_port+i, remote_host, remote_port, transport))
    for server in forward_servers:
        forwarding_threads.append(threading.Thread(target=server.serve_forever))
    for thread in forwarding_threads:
        thread.setDaemon(True)
        thread.start()
    print('Type "exit" to terminate.')
    stop = False
    while not stop:
        try:
            cmd = input(colored('(cpt) ', 'green'))
            if (cmd == "exit"):
                stop = True
        except KeyboardInterrupt:
            stop = True    
except Exception as e:
    print(str(e))
finally:
    print('Terminating...')
    # stop servers
    for server in forward_servers:
        server.shutdown()
    # waiting other threads for complete:
    for thread in forwarding_threads:
        thread.join()    
    print('Port forwarding stopped.')
    sys.exit(0)

