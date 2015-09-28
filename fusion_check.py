#!/usr/bin/env python

import argparse
import ConfigParser
import json
import os
import requests
import time
from keystoneclient.v2_0.client import Client as keystone_client


class FusionCheck(object):
    def __init__(self, username, tenant, password, auth_url, base_url):
        self.tenant = tenant
        self.fusion_url = ('{}/v1/{}'.format(base_url, tenant))
        keystone = keystone_client(username=username, password=password,
                                   tenant_name=tenant, auth_url=auth_url)
        self.token = keystone.auth_token
        self.headers = {'x-auth-user': username,
                        'x-auth-token': self.token,
                        'content-type': 'application/json',
                        'accept': 'application/json'}

    def get_catalog(self):
        start = time.time()
        r = requests.get(self.fusion_url +
                         '/templates?with_metadata=1&template_type=',
                         headers=self.headers)
        r.raise_for_status()
        self.catalog_time = time.time() - start
        self.catalog = r.json()

    def get_template(self, template_id):
        start = time.time()
        r = requests.get('{}/templates/{}'.format(self.fusion_url,
                         template_id), headers=self.headers)
        r.raise_for_status()
        self.template_time = time.time() - start
        repr(r.json())

    def get_template_params(self, template_id):
        start = time.time()
        r = requests.get('{}/template_params/{}'.format(self.fusion_url,
                         template_id), headers=self.headers)
        r.raise_for_status()
        self.template_params_time = time.time() - start
        repr(r.json())


def main():
    parser = argparse.ArgumentParser(description='Test fusion template '
                                     'catalog')
    parser.add_argument('-c', '--config', help='Path to config file',
                        default='/etc/heat-monitoring/fusion_check.cfg')
    parser.add_argument('-u', '--user', help='Username')
    parser.add_argument('-p', '--password', help='Password')
    parser.add_argument('-t', '--tenant', help='Tenant name')
    parser.add_argument('-a', '--auth_url', help='Authentication URL',
                        default='https://identity.api.rackspacecloud.com/v2.0/'
                        )
    parser.add_argument('-b', '--base_url', help='Base URL for Heat service',
                        default='https://iad.orchestration.api.rackspacecloud.'
                        'com')
    parser.add_argument('-e', '--endpoint', choices=['catalog', 'template',
                        'template_params', 'all'], default='all',
                        help='GET endpoint to time')

    args = parser.parse_args()
    config_file = args.config
    endpoint = args.endpoint

    config = ConfigParser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)

    username = args.user if args.user else config.get('fusion', 'username')
    password = args.password if args.password else config.get('fusion',
                                                              'password')
    tenant = args.tenant if args.tenant else config.get('fusion', 'tenant')
    auth_url = args.auth_url if args.auth_url else config.get('fusion',
                                                              'auth_url')
    base_url = args.base_url if args.base_url else config.get('fusion',
                                                              'base_url')

    fusion_check = FusionCheck(username, tenant, password, auth_url, base_url)
    fusion_check.get_catalog()
    if endpoint == 'catalog' or endpoint == 'all':
        time = fusion_check.catalog_time
        print('metric get_catalog float {:.3f}'.format(time))
    if endpoint == 'template' or endpoint == 'all':
        template_id = fusion_check.catalog['templates'][0]['id']
        fusion_check.get_template(template_id)
        time = fusion_check.template_time
        print('metric get_template float {:.3f}'.format(time))
    if endpoint == 'template_params' or endpoint == 'all':
        template_id = fusion_check.catalog['templates'][0]['id']
        fusion_check.get_template_params(template_id)
        time = fusion_check.template_params_time
        print('metric get_template_params float {:.3f}'.format(time))


if __name__ == '__main__':
    main()
