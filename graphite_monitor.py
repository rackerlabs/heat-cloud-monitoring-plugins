#!/usr/bin/env python

import argparse
import json
from httplib2 import Http, HttpLib2Error
from urllib import quote


def join_series(data):
    results = []
    if type(data) is dict:
        for key in iter(data.keys()):
            results += ['{}({})'.format(key, join_series(data[key]))]
    if type(data) is list:
        for item in data:
            results += [join_series(item)]
    if type(data) is str or type(data) is unicode:
        return data
    return ','.join(results)


def build_url(config):
    url = "{}/render/?from={}&format=json".format(config['graphite'],
                                                  config['time'])
    for target in config['targets']:
        url += "&target={}".format(quote(join_series(target)))
    return url

def _total_datapoints(datapoints, config):
    value = 0.0
    for (dp, ts) in datapoints:
        if dp:
            value += dp * config['multiplier']
    return value

def calculate_percentage(data, config):
    assert len(data) == 2, ('Two sets of datapoints are required to calculate '
                           'percentage')
    values = [_total_datapoints(target['datapoints'], config) for pos, target
              in enumerate(data)]
    if values[1] == 0.0:
        return 0.0
    return (values[0] / values[1]) * config['multiplier']

def calculate_count(data, config):
    assert len(data) == 1, ('One set of datapoints required when calculating '
                           'counts')
    return _total_datapoints(data[0]['datapoints'], config)

def calculate_average(data, config):
    assert len(data) == 1, ('One set of datapoints required when calculating '
                           'averages')
    datapoints = data[0]['datapoints']
    return _total_datapoints(datapoints, config) / len(datapoints)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='Path to config')
    args = parser.parse_args()

    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
        url = build_url(config)
        h = Http()
        resp, content = h.request(url)
        data = json.loads(content)
        value = 0
        if config['type'] == "sum":
            value = calculate_count(data, config)
        elif config['type'] == "percent":
            if len(data) < 2:
                print("metric {} 0.0".format(config['metric']))
                exit(0)
            value = calculate_percentage(data, config)
        elif config['type'] == "average":
            value = calculate_average(data, config)
        else:
            raise SyntaxError('Invalid calculation type')
    except (IOError, HttpLib2Error, AssertionError) as e:
        print('{}'.format(repr(e)))
        exit(1)

    print("metric {} {}".format(config['metric'], value))


if __name__ == "__main__":
    main()
