#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import argparse
import configparser
import json
import csv
import mimetypes

from io import StringIO

name = 'mattersend'
version = '2.0'
url = 'https://github.com/mtorromeo/mattersend'
description = "Library and CLI utility to send messages to mattermost's incoming webhooks"

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


def detect_syntax(basename, mime):
    if mime in mime_to_syntax:
        return mime_to_syntax[mime]

    (_, ext) = os.path.splitext(basename)
    if not ext:
        ext = basename
    return ext_to_syntax[ext] if ext in ext_to_syntax else None


def build(options, message):
    payload = {}

    # build request
    if message:
        payload['text'] = message

    for opt in ('channel', 'username', 'icon_url', 'icon_emoji'):
        if opt in options:
            payload[opt] = options[opt]

    return payload


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def md_table(data):
    md = []
    for i, row in enumerate(data):
        if i == 1:
            md.append("| --- " * len(row) + "|")
        md.append("| {} |".format(" | ".join(
            [str(cell).replace("|", "❘").replace("\n", " ").replace("\r", " ") for cell in row]
        )))
    return "\n".join(md)


def md_code(code, syntax='plain'):
    if syntax == 'plain':
        syntax = ''
    return "```{}\n{}```".format(syntax, code)


def main():
    try:
        import setproctitle
        setproctitle.setproctitle(name)
    except ImportError:
        pass

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

    if args.file == '-':
        message = sys.stdin.read()
        filename = None
    else:
        message = ''
        filename = args.file

    try:
        payload = send(args.channel, message, filename, args.url,
                       args.username, args.icon, args.syntax, args.tabular,
                       args.info, args.dry_run, args.section, name,
                       args.config)
    except (configparser.Error, TypeError, RuntimeError) as e:
        sys.exit(str(e))

    if args.dry_run:
        print(payload)


def send(channel, message='', filename=False, url=None, username=None,
         icon=None, syntax='auto', tabular=False, fileinfo=False,
         just_return=False, config_section='DEFAULT',
         config_name='mattersend', config_file=None):
    import requests

    # CONFIG file
    config = configparser.ConfigParser()

    if config_file:
        config.read(config_file)
    elif config_name:
        config.read(["/etc/{}.conf".format(config_name), os.path.expanduser("~/.{}.conf".format(config_name))])

    # merge config file with cli arguments
    options = {}
    for opt in ('channel', 'url', 'username', 'icon'):
        arg = locals()[opt]
        if arg:
            options[opt] = arg
        elif opt in config[config_section]:
            options[opt] = config[config_section][opt]
        elif config_section != 'DEFAULT' and opt in config['DEFAULT']:
            options[opt] = config['DEFAULT'][opt]

    if 'url' not in options:
        raise TypeError('Missing mattermost webhook URL')

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

    if not filename or tabular:
        syntax = None

    # read message from CLI or stdin
    if filename:
        (mime, _) = mimetypes.guess_type(filename)
        basename = os.path.basename(filename)

        with open(filename, 'rU') as f:
            filecontents = f.read()
            if message:
                message += "\n\n" + filecontents
            else:
                message = filecontents

    if tabular:
        csvfile = StringIO(message.strip())

        if tabular == 'sniff':
            dialect = csv.Sniffer().sniff(message)
        else:
            dialect = tabular

        message = md_table(csv.reader(csvfile, dialect))

    elif syntax == 'auto':
        syntax = detect_syntax(basename, mime)

    if syntax is not None:
        message = md_code(message, syntax)

    if filename and fileinfo:
        statinfo = os.stat(filename)
        message = md_table([
            ['Filename', 'Size', 'Mime'],
            [basename, sizeof_fmt(statinfo.st_size), mime],
        ]) + "\n\n" + message

    payload = build(options, message.strip())
    payload = json.dumps(payload, sort_keys=True, indent=4)

    if just_return:
        return "POST {}\n{}".format(options['url'], payload)

    r = requests.post(options['url'], data={'payload': payload})

    if r.status_code != 200:
        try:
            r = json.loads(r.text)
        except json.decoder.JSONDecodeError:
            r = {'message': r.text, 'status_code': r.status_code}
        raise RuntimeError("{} ({})".format(r['message'], r['status_code']))

if __name__ == '__main__':
    main()
