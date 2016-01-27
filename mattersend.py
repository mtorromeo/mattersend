#!/usr/bin/env python
# -*- coding:utf-8 -*-

name = 'mattersend'
version = '1.0'
url = 'https://github.com/mtorromeo/mattersend'
description = "Sends messages to mattermost's incoming webhooks via CLI"


def build(options, args, message):
    payload = {}

    # build request
    if message:
        payload['text'] = message

    for opt in ('channel', 'username', 'icon_url', 'icon_emoji'):
        if opt in options:
            payload[opt] = options[opt]

    return payload


def main():
    import sys
    import os
    import argparse
    import configparser
    import json

    import setproctitle
    import requests

    setproctitle.setproctitle(name)

    # CLI arguments
    parser = argparse.ArgumentParser(prog=name, description=description)

    parser.add_argument('-V', '--version',  action='version', version="%(prog)s " + version)
    parser.add_argument('-C', '--config',   help='Use a different configuration file')
    parser.add_argument('-s', '--section',  help='Configuration file section', default='DEFAULT')
    parser.add_argument('-c', '--channel',  help='Send to this channel or @username')
    parser.add_argument('-U', '--url',      help='Mattermost webhook URL')
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-i', '--icon',     help='Icon')
    parser.add_argument('message', nargs='?', help='The message to send. '
                        'If not specified it will be read from STDIN')

    args = parser.parse_args()

    # CONFIG file
    config = configparser.SafeConfigParser()
    try:
        if args.config:
            config.read(args.config)
        else:
            config.read(["/etc/{}.conf".format(name), os.path.expanduser("~/.{}.conf".format(name))])
    except configparser.Error as e:
        sys.exit(e.message)

    # merge config file with cli arguments
    options = {}
    for opt in ('channel', 'url', 'username', 'icon'):
        arg = getattr(args, opt)
        if arg:
            options[opt] = arg
        elif opt in config[args.section]:
            options[opt] = config[args.section][opt]
        elif args.section != 'DEFAULT' and opt in config['DEFAULT']:
            options[opt] = config['DEFAULT'][opt]

    if 'url' not in options:
        sys.exit('Missing mattermost webhook URL')

    if 'icon' in options:
        ioptname = 'icon_url' if '://' in options['icon'] else 'icon_emoji'
        options[ioptname] = options['icon']
        del options['icon']

    # read message from CLI or stdin
    message = args.message if args.message else sys.stdin.read()
    payload = build(options, args, message)
    r = requests.post(options['url'], data={'payload': json.dumps(payload)})

    if r.status_code != 200:
        try:
            r = json.loads(r.text)
        except json.decoder.JSONDecodeError:
            r = {'message': r.text, 'status_code': r.status_code}
        sys.exit("{} ({})".format(r['message'], r['status_code']))

if __name__ == '__main__':
    main()
