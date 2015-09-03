#!/usr/bin/env python

import ConfigParser
import argparse
import os
import time

from keystoneclient.v2_0.client import Client as keystone_client
from heatclient.client import Client as heat_client
from heatclient.exc import *


class HeatCheck(object):
    def __init__(self, username, password, tenant, auth_url, heat_url, region):
        self.username = username
        self.password = password
        self.tenant = tenant
        self.auth_url = auth_url
        self.heat_url = heat_url
        self.region = region
        self.stack_list = []

        keystone = keystone_client(username=self.username,
                                   password=self.password,
                                   tenant_name=self.tenant,
                                   auth_url=self.auth_url)
        self.token = keystone.auth_token
        self.heat = heat_client('1', endpoint=self.heat_url,
                                region_name=self.region, token=self.token,
                                insecure=True)

    def build_info_time(self):
        try:
            start = time.time()
            build_info = self.heat.build_info.build_info()
            return time.time() - start
        except BaseException, e:
            print(e)
            return None

    def stack_list_time(self):
        try:
            start = time.time()
            self.stack_list = list(self.heat.stacks.list())
            return time.time() - start
        except BaseException, e:
            print(e)
            return None

    def stack_show_time(self):
        try:
            if len(self.stack_list) > 0:
                start = time.time()
                stack_show = self.heat.stacks.get(self.stack_list[0].id)
                return time.time() - start
            return None
        except BaseException, e:
            print(e)
            return None

    def stack_preview_time(self, template_url, parameters=None):
        if parameters:
            kwargs = {'stack_name': 'test', 'template_url': template_url,
                      'parameters': parameters}
        else:
            kwargs = {'stack_name': 'test', 'template_url': template_url}

        try:
            start = time.time()
            stack = self.heat.stacks.preview(**kwargs)
            return time.time() - start
        except BaseException, e:
            print(e)
            return None


def main():
    parser = argparse.ArgumentParser(description='Test a heat endpoint')
    parser.add_argument('-c', '--config', help='Path to config file',
                        default='/etc/heat-monitoring/heat_check.cfg')
    parser.add_argument('-e', '--env', help='Environment settings to get from '
                        'config')
    parser.add_argument('-u', '--user', help='Username')
    parser.add_argument('-p', '--password', help='Password')
    parser.add_argument('-t', '--tenant', help='Tenant name')
    parser.add_argument('-a', '--auth_url', help='Authentication URL',
                        default='https://identity.api.rackspacecloud.com/v2.0/'
                        )
    parser.add_argument('-U', '--heat_url', help='URL for Heat service')
    parser.add_argument('-r', '--region', help='Region for service catalog')
    parser.add_argument('-T', '--template', choices=['wp_single', 'wp_multi',
                        'django_clouddb'], default='wp_single',
                        help='Template for stack preview')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--basic', action='store_false', help='Runs '
                       'build_info, stack_list, and stack_show times')
    group.add_argument('-P', '--preview', action='store_true', help='Runs '
                       'stack preview times for three templates')

    args = parser.parse_args()
    config_file = args.config
    section = args.env

    config = ConfigParser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)

    username = args.user if args.user else config.get(section, 'username')
    password = args.password if args.password else config.get(section,
                                                              'password')
    tenant_name = args.tenant if args.tenant else config.get(section, 'tenant')
    auth_url = args.auth_url if args.auth_url else config.get(section,
                                                              'auth_url')
    heat_url = args.heat_url if args.heat_url else config.get(section,
                                                              'heat_url')
    region = args.region if args.region else config.get(section, 'region')

    keystone = keystone_client(username=username, password=password,
                               tenant_name=tenant_name, auth_url=auth_url)
    token = keystone.auth_token
    heat = heat_client('1', endpoint=heat_url, region_name=region, token=token)

    check = HeatCheck(username, password, tenant_name, auth_url, heat_url,
                      region)

    if args.preview:
        preview_templates = {
            'wp_single': 'https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-single/master/wordpress-single.yaml',
            'wp_multi': 'https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-multi-server.yaml',
            'django_clouddb': 'https://raw.githubusercontent.com/rackspace-orchestration-templates/django-clouddb/master/django-multi.yaml'
        }

        template = args.template
        url = preview_templates[template]

        if template == 'django_clouddb':
            preview_time = check.stack_preview_time(url,
                                                    parameters={'datastore_version': '5.1'})
        else:
            preview_time = check.stack_preview_time(url)

        print('metric preview_{} float {}'.format(template, preview_time))
    else:
        bi_time = check.build_info_time()
        sl_time = check.stack_list_time()
        ss_time = check.stack_show_time()

        print('metric build_info float {}'.format(bi_time))
        print('metric stack_list float {}'.format(sl_time))
        print('metric stack_show float {}'.format(ss_time))


if __name__ == '__main__':
    main()
