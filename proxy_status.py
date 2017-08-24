#!/usr/bin/env python

import argparse
import csv
import socket
import sys


DEFAULT_SOCKET = '/var/lib/haproxy/stats'
RECV_SIZE = 1024

class HAProxySocket(object):
    def __init__(self, socket_file=DEFAULT_SOCKET):
        self.socket_file = socket_file

    def connect(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket_file)
        return s
    
    def communicate(self, command):
        ''' Send a single command to the socket and return a single response (raw string) '''
        s = self.connect()
        if not command.endswith('\n'): command += '\n'
        s.send(command)
        result = ''
        buf = ''
        buf = s.recv(RECV_SIZE)
        while buf:
            result += buf
            buf = s.recv(RECV_SIZE)
        s.close()
        return result
    
    def get_server_info(self):
        result = {}
        output = self.communicate('show info')
        for line in output.splitlines():
            try:
                key,val = line.split(':')
            except ValueError:
                continue
            result[key.strip()] = val.strip()
        return result
    
    def get_server_stats(self):
        output = self.communicate('show stat')
        #sanitize and make a list of lines
        output = output.lstrip('# ').strip()
        output = [ l.strip(',') for l in output.splitlines() ]
        csvreader = csv.DictReader(output)
        result = [ d.copy() for d in csvreader ]
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('proxy', help='Name of the proxy that should be checked')
    parser.add_argument('-s', '--socket', default='/var/lib/haproxy/stats', help='Path to HAProxy stats socket')
    args = parser.parse_args()

    proxy_name = args.proxy
    haproxy_socket = args.socket

    haproxy = HAProxySocket(haproxy_socket)
    try:
        stats = haproxy.get_server_stats()
    except Exception, e:
        print("status Failed to get server stats: %r" % e)
        sys.exit(1)

    nodes = [node for node in stats if node['pxname'] == proxy_name and node['svname'] != 'FRONTEND' and node['svname'] != 'BACKEND']
    nodes_up = 0
    nodes_down = 0
    sessions = 0
    for node in nodes:
        if node['status'] == 'UP':
            nodes_up += 1
        elif node['status'] == 'DOWN':
            nodes_down += 1
        sessions += int(node['scur'])

    print("metric nodes_up int %i" % nodes_up)
    print("metric nodes_down int %i" % nodes_down)
    print("metric sessions int %i" % sessions)


if __name__ == "__main__":
    main()
