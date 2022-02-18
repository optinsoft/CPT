#!/usr/bin/env python

# Copyright (c) 2022 Vitaly Yakovlev <vitaly@optinsoft.net>
#
# CPT.py
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
import sys, os
from termcolor import colored
import argparse
import ipaddress
from dotenv import load_dotenv
import json
from cptutils import CommandHandler

def forward_tunnel_server(local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHander(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
    server = ForwardServer(("", local_port), SubHander)
    server.local_port = local_port
    server.remote_host = remote_host
    server.remote_port = remote_port
    return server

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="CPT.py")

    parser.add_argument('--config', help='path to the configuration file (JSON); you can either provide command line arguments to cpt.py or use the configuration file')

    parser.add_argument('--local-port', type=int, help='local (client) port is to be forwarded to the REMOTE_IP:REMOTE_PORT')
    parser.add_argument('--remote-ip', help='remote host IP')
    parser.add_argument('--remote-port', type=int, help='remote host port')
    parser.add_argument('--count', default=1, type=int, help='count of the forwarded ports; first local port will be forwarded to the REMOTE_IP:REMOTE_PORT, second - to the REMOTE_IP+1:REMOTE_PORT, etc.')
    parser.add_argument('--ssh-host', help='SSH host')
    parser.add_argument('--ssh-port', default=22, type=int, help='SSH port')
    parser.add_argument('--ssh-user', help='SSH user')
    parser.add_argument('--ssh-keyfile', help='SSH private key file')

    args = parser.parse_args()

    if (args.config):
        with open(args.config, 'rt') as f:
            t_args = argparse.Namespace()
            t_args.__dict__.update(json.load(f))
            args = parser.parse_args(namespace=t_args)

    required_arg_names = ['local_port', 'remote_ip', 'remote_port', 
        'count', 'ssh_host', 'ssh_port', 'ssh_user', 'ssh_keyfile']
    vargs = vars(args)
    missed_args = ", ".join(filter(lambda name : vargs[name] is None, required_arg_names))

    if (missed_args):
        parser.print_usage()
        print("error: the following arguments are required: ", missed_args)
        sys.exit(0)

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

    for i in range(0, count):        
        remote_host = str(remote_ip + i)
        forward_servers.append(forward_tunnel_server(local_port+i, remote_host, remote_port, transport))

    cmdhandler = CommandHandler(forward_servers)

    try:
        for server in forward_servers:
            forwarding_threads.append(threading.Thread(target=server.serve_forever))
        print("Start forwarding...")
        for thread in forwarding_threads:
            thread.setDaemon(True)
            thread.start()
        cmdhandler.print_hint()
        while not cmdhandler.terminated:
            try:
                cmd = input(colored('(cpt) ', 'green'))
                cmdhandler.handle(cmd)
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

if __name__ == "__main__":
    main()