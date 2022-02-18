# Copyright (c) 2022 Vitaly Yakovlev <vitaly@optinsoft.net>
#
# This file is part of CPT.py

import re
from termcolor import colored
import os

class Command:
    def __init__(self, handler, description = ""):
        self.handler = handler
        self.description = description

class CommandHandler:

    cmd_re = re.compile("^\\s*([a-zA-Z_][a-zA-Z0-9-_']*)(\s+.*$|$)")

    def __init__(self, forward_servers):
        self.forward_servers = forward_servers
        self.commands = {
            "exit": Command(handler=self.handle_exit, description="Terminate forwarding and exit."),
            "help": Command(handler=self.handle_help, description="Display this message."),
            "list": Command(handler=self.handle_list, description="List forwards"),
            "adb-connect": Command(handler=self.handle_adb_connect, description="Run for all local ports: adb connect 127.0.0.1:<local_port>"),
            "adb-disconnect": Command(handler=self.handle_adb_disconnect, description="Run for all local ports: adb disconnect 127.0.0.1:<local_port>"),
            "adb-devices": Command(handler=self.handle_adb_devices, description="Run: adb devices"),
            "adb-push": Command(handler=self.handle_adb_push, description="Run for all local ports: adb -s 127.0.0.1:<local_port> push ..."),
            "adb-shell": Command(handler=self.handle_adb_shell, description="Run for all local ports: adb -s 127.0.0.1:<local_port> adb shell ...")
        }
        self.unknown_command = Command(handler=self.handle_unknown, description="unknown command")
        self.terminated = False

    def handle_exit(self, cmd_name, cmd_args):
        self.terminated = True

    def handle_help(self, cmd_name, cmd_args):
        m = self.cmd_re.match(cmd_args)
        if (m):
            help_cmd_name = m.group(1)
            help_command = self.commands.get(help_cmd_name, self.unknown_command)
            print(help_command.description)
            return
        print("Commands:")
        for name in self.commands:
            print("  " + name)
        print("Please type \"help <command>\" to see description of the <command>")

    def handle_unknown(self, cmd_name, cmd_args):
        print(colored("unknown command: " + cmd_name))

    def handle_bad_command(self, cmd):
        print(colored("bad command", "red"))

    def handle(self, cmd):
        m = self.cmd_re.match(cmd)
        if m:
            cmd_name = m.group(1)
            cmd_args = m.group(2)
            command = self.commands.get(cmd_name, self.unknown_command)
            command.handler(cmd_name, cmd_args.lstrip())
        else:
           self.handle_bad_command(cmd)
    
    def print_hint(self):
        print('Type "exit" to terminate. Type "help" to view list of commands.')

    def handle_list(self, cmd_name, cmd_args):
        for server in self.forward_servers:
            print(str(server.local_port) + ' -> ' + server.remote_host)

    def run_os_cmd(self, os_cmd):
        print(colored("run: ", "green") + os_cmd)
        os.system(os_cmd)

    def handle_adb_connect(self, cmd_name, cmd_args):
        for server in self.forward_servers:
            self.run_os_cmd("adb connect 127.0.0.1:"+str(server.local_port))

    def handle_adb_disconnect(self, cmd_name, cmd_args):
        for server in self.forward_servers:
            self.run_os_cmd("adb disconnect 127.0.0.1:"+str(server.local_port))

    def handle_adb_devices(self, cmd_name, cmd_args):
        self.run_os_cmd("adb devices")

    def handle_adb_push(self, cmd_name, cmd_args):
        for server in self.forward_servers:
            self.run_os_cmd("adb -s 127.0.0.1:"+str(server.local_port)+" push "+cmd_args)

    def handle_adb_shell(self, cmd_name, cmd_args):
        for server in self.forward_servers:
            self.run_os_cmd("adb -s 127.0.0.1:"+str(server.local_port)+" shell "+cmd_args)