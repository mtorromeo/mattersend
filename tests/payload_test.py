import re
import mattersend
from pyfakefs import fake_filesystem_unittest

try:
    from unittest import mock
except ImportError:
    import mock


def normalize_payload(payload):
    lines = []
    for line in payload.splitlines():
        lines.append(line.rstrip())
    return "\n".join(lines)


class MockResponse:
    def __init__(self, url, data):
        self.text = 'test'
        if url.endswith('/fail'):
            self.status_code = 502


class PayloadTest(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.CreateFile('/etc/mattersend.conf', contents='''[DEFAULT]
url=https://chat.mydomain.com/hooks/abcdefghi123456

[angrybot]
icon = :angry:
username = AngryBot''')
        self.fs.CreateFile('/etc/mime.types', contents='text/x-diff diff')
        self.fs.CreateFile('/home/test/source.coffee', contents='x' * 5000)
        self.fs.CreateFile('/home/test/source.csv',
                           contents='abc,def\nfoo,bar')
        self.fs.CreateFile('/home/test/source.diff')
        self.fs.CreateFile('/home/test/Makefile')

    def test_simple_1(self):
        payload = mattersend.send(channel='town-square',
                                  message='test message',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "text": "test message"
}""")

    def test_section(self):
        payload = mattersend.send(channel='town-square',
                                  message='test message',
                                  config_section='angrybot',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "icon_url": "https://chat.mydomain.com/static/images/emoji/angry.png",
    "text": "test message",
    "username": "AngryBot"
}""")

    def test_override_url(self):
        payload = mattersend.send(channel='town-square',
                                  message='test message',
                                  url='http://chat.net/hooks/abdegh12',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST http://chat.net/hooks/abdegh12
{
    "channel": "town-square",
    "text": "test message"
}""")

    def test_syntax_by_ext(self):
        payload = mattersend.send(channel='town-square',
                                  filename='/home/test/source.coffee',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "text": "```coffeescript\n%s```"
}""" % ('x' * 5000))

    def test_syntax_by_mime(self):
        payload = mattersend.send(channel='town-square',
                                  filename='/home/test/source.diff',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "text": "```diff\n```"
}""")

    def test_syntax_mk(self):
        payload = mattersend.send(channel='town-square',
                                  filename='/home/test/Makefile',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "text": "```makefile\n```"
}""")

    def test_filename_and_message(self):
        payload = mattersend.send(channel='town-square',
                                  filename='/etc/mime.types',
                                  message='test message',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "text": "test message\n\ntext/x-diff diff"
}""")

    def test_fileinfo(self):
        payload = mattersend.send(channel='town-square',
                                  filename='/home/test/source.coffee',
                                  fileinfo=True,
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "text": "| Filename | Size | Mime |\n| --- | --- | --- |\n| source.coffee | 4.9KiB | None |\n\n```coffeescript\n%s```"
}""" % ('x' * 5000))

    def test_csv(self):
        payload = mattersend.send(channel='town-square',
                                  filename='/home/test/source.csv',
                                  tabular='sniff',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "text": "| abc | def |\n| --- | --- |\n| foo | bar |"
}""")

    def test_csv_dialect(self):
        payload = mattersend.send(channel='town-square',
                                  filename='/home/test/source.csv',
                                  tabular='excel',
                                  just_return=True)

        self.assertEqual(normalize_payload(payload),
                         r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town-square",
    "text": "| abc | def |\n| --- | --- |\n| foo | bar |"
}""")

    @mock.patch('requests.post', side_effect=MockResponse)
    def test_send(self, mock_post):
        payload = mattersend.send(channel='town-square',
                                  message='test message',
                                  url='http://chat.net/hooks/abdegh12')

    @mock.patch('requests.post', side_effect=MockResponse)
    def test_send(self, mock_post):
        with self.assertRaises(RuntimeError):
            payload = mattersend.send(channel='town-square',
                                      message='test message',
                                      url='http://chat.net/hooks/fail')
