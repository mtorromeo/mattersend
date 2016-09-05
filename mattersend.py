#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import argparse
import json
import csv
import mimetypes

from io import StringIO

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

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


class Message:
    def __init__(self, channel=None, url=None, username=None, icon=None,
                 config_section='DEFAULT', config_name='mattersend',
                 config_file=None):
        # CONFIG file
        config = configparser.ConfigParser()

        if config_file:
            config.read(config_file)
        elif config_name:
            config.read(["/etc/{}.conf".format(config_name), os.path.expanduser("~/.{}.conf".format(config_name))])

        config = dict(config.items(config_section))

        # merge config file with cli arguments
        self.url = config.get('url') if url is None else url
        self.channel = config.get('channel') if channel is None else channel
        self.username = config.get('username') if username is None else username
        self.icon = config.get('icon') if icon is None else icon

        self.text = ''
        self.attachments = []

    def get_payload(self):
        payload = {}

        for opt in ('text', 'channel', 'username'):
            optvalue = getattr(self, opt)
            if optvalue is not None:
                payload[opt] = optvalue.strip()

        opt, optvalue = self.get_icon()
        if optvalue is not None:
            payload[opt] = optvalue

        if self.attachments:
            payload['attachments'] = [a.data() for a in self.attachments]

        return json.dumps(payload, sort_keys=True, indent=4)

    def get_icon(self):
        if self.icon is None:
            return None, None

        ioptvalue = self.icon.strip()
        ioptname = 'icon_url' if '://' in ioptvalue else 'icon_emoji'

        # workaround mattermost missing icon_emoji until implemented
        if ioptname == 'icon_emoji' and ioptvalue[0] == ':' and ioptvalue[-1] == ':':
            baseurl = self.url.split('/hooks/', 1)
            if len(baseurl) == 2:
                ioptname = 'icon_url'
                ioptvalue = "{}/static/images/emoji/{}.png".format(baseurl[0], ioptvalue[1:-1])

        return ioptname, ioptvalue

    def append(self, text, separator=None):
        if self.text and separator is not None:
            self.text += separator
        self.text += text

    def attach_file(self, filename, text=None, tabular=False, syntax='auto', fileinfo=False):
        attachment = Attachment()

        if tabular:
            syntax = None

        (mime, _) = mimetypes.guess_type(filename)
        attachment.title = os.path.basename(filename)

        if text is None:
            with open(filename, 'rUb') as f:
                text = f.read().decode('utf-8')

        if tabular:
            csvfile = StringIO(text.strip())

            if tabular == 'sniff':
                dialect = csv.Sniffer().sniff(text)
            else:
                dialect = tabular

            text = md_table(csv.reader(csvfile, dialect))

        elif syntax == 'auto':
            syntax = detect_syntax(attachment.title, mime)

        if syntax is not None:
            text = md_code(text, syntax)

        attachment.text = text

        if fileinfo:
            statinfo = os.stat(filename)
            attachment.add_field('Size', sizeof_fmt(statinfo.st_size), True)
            attachment.add_field('Mime', mime, True)

        self.attachments.append(attachment)
        return attachment

    def send(self):
        if self.url is None:
            raise TypeError('Missing mattermost webhook URL')

        if self.channel is None:
            raise TypeError('Missing destination channel')

        import requests

        payload = self.get_payload()
        r = requests.post(self.url, data={'payload': payload})

        if r.status_code != 200:
            try:
                r = json.loads(r.text)
            except ValueError:
                r = {'message': r.text, 'status_code': r.status_code}
            raise RuntimeError("{} ({})".format(r['message'], r['status_code']))

        return r


class Attachment:
    def __init__(self, text=''):
        self.text = text
        self.color = None
        self.pretext = None
        self.fallback = None

        self.author_name = None
        self.author_link = None
        self.author_icon = None

        self.title = None
        self.title_link = None

        self.image_url = None
        self.thumb_url = None

        self.fields = []

    def set_author(self, name, link=None, icon=None):
        self.author_name = name
        self.author_link = link
        self.author_icon = icon

    def set_title(self, title, link=None):
        self.title = title
        self.title_link = link

    def add_field(self, title, value, short=None):
        field = {
            'title': str(title),
            'value': str(value),
        }
        if short is not None:
            field['short'] = bool(short)
        self.fields.append(field)

    def data(self):
        data = {k: v for (k, v) in self.__dict__.items() if v}
        if not self.fallback:
            data['fallback'] = self.text
        # 4000+ chars triggers error on mattermost, not sure where the limit is
        data['text'] = data['text'][:3500]
        data['fallback'] = data['fallback'][:3500]
        return data


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
    msg = Message(channel, url, username, icon, config_section,
                  config_name, config_file)

    if filename:
        if syntax == 'none':
            syntax = None
        msg.attach_file(filename, None, tabular, syntax, fileinfo)
    else:
        if tabular:
            syntax = None
            csvfile = StringIO(message.strip())

            if tabular == 'sniff':
                dialect = csv.Sniffer().sniff(message)
            else:
                dialect = tabular

            message = md_table(csv.reader(csvfile, dialect))

        elif syntax in ('auto', 'none'):
            syntax = None

        if syntax is not None:
            message = md_code(message, syntax)

    msg.text = message

    if just_return:
        payload = msg.get_payload()
        return "POST {}\n{}".format(msg.url, payload)

    msg.send()


if __name__ == '__main__':
    main()
