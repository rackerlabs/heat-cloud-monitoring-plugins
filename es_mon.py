#!/usr/bin/env python

import argparse
from elasticsearch import Elasticsearch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='localhost',
                        help='Elasticsearch host')
    parser.add_argument('-P', '--port', default=9200, help='Elasticsearch '
                        'HTTP port')
    parser.add_argument('-s', '--ssl', default=False, action='store_true',
                        help='Use SSL for connection')
    parser.add_argument('-u', '--username', help='HTTP auth username')
    parser.add_argument('-p', '--password', help='HTTP auth password')
    parser.add_argument('-U', '--url_prefix', default='', help='URL prefix '
                        'for HTTP requests')
    parser.add_argument('-i', '--index', default='_all', help='Index that '
                        'should be searched. Default: _all')
    parser.add_argument('-f', '--field', default='@timestamp', help='Field the '
                        'range should be bound to. Default: @timestamp')
    parser.add_argument('-r', '--range', default='now-1h', help='Start time to '
                        'search back for entries. Default: now-1h')
    args = parser.parse_args()

    host = args.host
    port = args.port
    ssl = args.ssl
    username = args.username
    password = args.password
    url_prefix = args.url_prefix
    index = args.index
    field = args.field
    time = args.range

    hosts = [{
        'host': host,
        'port': port,
        'url_prefix': url_prefix,
        'http_auth': '{}:{}'.format(username, password),
        'use_ssl': ssl
    },]
    es = Elasticsearch(hosts)
    search_filter = {
        'query': {
            'filtered': {
                'filter': {
                    'range': {
                        field: {
                            'gte': time
                        }
                    }
                }
            }
        }
    }
    count = es.count(index=index, body=search_filter)
    print 'metric item_count int {}'.format(count['count'])


if __name__ == "__main__":
    main()