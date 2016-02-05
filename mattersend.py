#!/usr/bin/env python
# -*- coding:utf-8 -*-

name = 'mattersend'
version = '1.2'
url = 'https://github.com/mtorromeo/mattersend'
description = "Sends messages to mattermost's incoming webhooks via CLI"

syntaxes = ['diff', 'apache', 'makefile', 'http', 'json', 'markdown',
            'javascript', 'css', 'nginx', 'objectivec', 'python', 'xml',
            'perl', 'bash', 'php', 'coffeescript', 'cs', 'cpp', 'sql', 'go',
            'ruby', 'java', 'ini', 'latex', 'plain', 'auto']

mime_to_syntax = {
    'text/x-diff': 'diff',
    'application/json': 'json',
    'application/x-javascript': 'javascript',
    'text/x-python': 'python',
    'application/xml': 'xml',
    'text/x-perl': 'perl',
    'text/x-sh': 'bash',
    'text/x-csrc': 'cpp',
    'text/x-chdr': 'cpp',
    'text/x-c++src': 'cpp',
    'text/x-c++hdr': 'cpp',
    'text/x-c': 'cpp',
    'application/x-sql': 'sql',
    'application/x-ruby': 'ruby',
    'text/x-java-source': 'java',
    'application/x-latex': 'latex',
}

ext_to_syntax = {
    'Makefile': 'makefile',
    '.mk': 'makefile',
    '.htaccess': 'apache',
    '.json': 'json',
    '.md': 'markdown',
    '.js': 'javascript',
    '.css': 'css',
    '.m': 'objectivec',
    '.py': 'python',
    '.xml': 'xml',
    '.pl': 'perl',
    '.sh': 'bash',
    '.php': 'php',
    '.phtml': 'php',
    '.phps': 'php',
    '.php3': 'php',
    '.php4': 'php',
    '.php5': 'php',
    '.php7': 'php',
    '.coffee': 'coffeescript',
    '.cs': 'cs',
    '.c': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.cpp': 'cpp',
    '.h': 'cpp',
    '.hh': 'cpp',
    '.dic': 'cpp',
    '.sql': 'sql',
    '.go': 'go',
    '.rb': 'ruby',
    '.java': 'java',
    '.ini': 'ini',
    '.latex': 'latex',
}


def build(options, args, message):
    payload = {}

    # build request
    if message:
        payload['text'] = message

    for opt in ('channel', 'username', 'icon_url', 'icon_emoji'):
        if opt in options:
            payload[opt] = options[opt]

    return payload


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def main():
    import sys
    import os
    import argparse
    import configparser
    import json
    import csv
    import mimetypes

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

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--tabular', metavar='DIALECT', const='sniff',
                       nargs='?', choices=dialects,
                       help='Parse input as CSV and format it as a table (DIALECT can be one of %(choices)s)')
    group.add_argument('-y', '--syntax', default='auto')

    parser.add_argument('-I', '--info', action='store_true',
                        help='Include file information in message')
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

        # workaround mattermost missing icon_emoji until implemented
        if ioptname == 'icon_emoji' and options['icon'][0] == ':' and options['icon'][-1] == ':':
            baseurl = options['url'].split('/hooks/', 1)
            if len(baseurl) == 2:
                ioptname = 'icon_url'
                options['icon'] = "{}/static/images/emoji/{}.png".format(baseurl[0], options['icon'][1:-1])

        options[ioptname] = options['icon']
        del options['icon']

    # read message from CLI or stdin
    if args.file == '-':
        message = sys.stdin.read()
        args.syntax = None
    else:
        (mime, _) = mimetypes.guess_type(args.file)
        basename = os.path.basename(args.file)

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
    elif args.syntax == 'auto':
        if mime in mime_to_syntax:
            args.syntax = mime_to_syntax[mime]
        else:
            (_, ext) = os.path.splitext(basename)
            if not ext:
                ext = basename
            if ext in ext_to_syntax:
                args.syntax = ext_to_syntax[ext]
            else:
                args.syntax = None

    if args.syntax is not None:
        message = "```{}\n{}```".format('' if args.syntax == 'plain' else args.syntax, message)

    if args.file != '-' and args.info:
        statinfo = os.stat(args.file)
        message = '''| Filename | Size | Mime |
| --- | --- | --- |
| {} | {} | {} |

'''.format(basename, sizeof_fmt(statinfo.st_size), mime) + message

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
