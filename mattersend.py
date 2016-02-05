#!/usr/bin/env python
# -*- coding:utf-8 -*-

name = 'mattersend'
version = '1.1'
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
    import csv

    import setproctitle
    import requests

    from io import StringIO

    setproctitle.setproctitle(name)
    dialects = csv.list_dialects()
    dialects.sort()
    dialects.insert(0, 'sniff')

    # CLI arguments
    parser = argparse.ArgumentParser(prog=name, description=description)

    parser.add_argument('-V', '--version',  action='version', version="%(prog)s " + version)
    parser.add_argument('-C', '--config',   help='Use a different configuration file')
    parser.add_argument('-s', '--section',  help='Configuration file section', default='DEFAULT')
    parser.add_argument('-c', '--channel',  help='Send to this channel or @username')
    parser.add_argument('-U', '--url',      help='Mattermost webhook URL')
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-i', '--icon',     help='Icon')
    parser.add_argument('-t', '--tabular', metavar='DIALECT', const='sniff', nargs='?',
                        help='Parse input as CSV and format it as a table (DIALECT can be one of {})'
                        .format(", ".join(dialects)))
    parser.add_argument('-n', '--dry-run', '--just-print', action='store_true',
                        help="Don't send, just print the payload")
    parser.add_argument('-f', '--file', default='-',
                        help="Read content from FILE. If - reads from standard input (DEFAULT: %(default)s)")

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

    if args.tabular and args.tabular not in dialects:
        sys.exit("Invalid dialect {}".format(args.tabular))

    # read message from CLI or stdin
    if args.file == '-':
        message = sys.stdin.read()
    else:
        with open(args.file, 'rU') as f:
            message = f.read()

    if args.tabular:
        csvfile = StringIO(message.strip())

        if args.tabular == 'sniff':
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(message)
            has_header = sniffer.has_header(message)
        else:
            dialect = args.tabular
            has_header = True

        message = []
        for i, row in enumerate(csv.reader(csvfile, dialect)):
            if i == 1 and has_header:
                message.append("| --- " * len(row) + "|")
            message.append("| {} |".format(" | ".join(
                [cell.replace("|", "❘").replace("\n", " ").replace("\r", " ") for cell in row]
            )))
        message = "\n".join(message)

    payload = build(options, args, message)

    if args.dry_run:
        print("POST {}".format(options['url']))
        print(json.dumps(payload, sort_keys=True, indent=4))
        sys.exit(0)

    r = requests.post(options['url'], data={'payload': json.dumps(payload, sort_keys=True)})

    if r.status_code != 200:
        try:
            r = json.loads(r.text)
        except json.decoder.JSONDecodeError:
            r = {'message': r.text, 'status_code': r.status_code}
        sys.exit("{} ({})".format(r['message'], r['status_code']))

if __name__ == '__main__':
    main()
