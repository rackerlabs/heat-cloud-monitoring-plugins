#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin to provide memcached statistics.

Copyright 2013 Steve Katen <steve.katen@rackspace.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import re
import socket
import sys
import telnetlib


def memcached_stats(host, port):
    regex = re.compile(ur"STAT (.*) (.*)\r")
    try:
        c = telnetlib.Telnet(host, port)
    except socket.error:
        return
    else:
        c.write("stats\n")
        return dict(regex.findall(c.read_until('END')))


def hit_percent(hits, misses):
    total = hits + misses
    if total > 0:
        return 100 * float(hits) / float(total)
    else:
        return 0.0


def fill_percent(used, total):
    return float(used / total)


def main():
    parser = argparse.ArgumentParser(description='Connects to memcached on '
                                     'specified host via telnet and returns '
                                     'several key stats.')
    parser.add_argument('-H', '--host', default='127.0.0.1', help='Hostname '
                        'or IP. Default: 127.0.0.1')
    parser.add_argument('-p', '--port', default='11211', help='Service port. '
                        'Default: 11211')
    args = parser.parse_args()

    s = memcached_stats(args.host, args.port)

    if not s:
        print "status err unable to generate statistics"
        sys.exit(1)

    print "status ok memcached statistics generated"
    print "metric uptime int", s['uptime']
    print "metric curr_connections int", s['curr_connections']
    print "metric listen_disabled_num int", s['listen_disabled_num']
    print "metric curr_items int", s['curr_items']
    print "metric total_items int", s['total_items']
    print "metric evictions int", s['evictions']
    print "metric hit_percent float", hit_percent(int(s['get_hits']),
                                                  int(s['get_misses']))
    print "metric fill_percent float", fill_percent(int(s['bytes']),
                                                    int(s['limit_maxbytes']))


if __name__ == '__main__':
    main()
