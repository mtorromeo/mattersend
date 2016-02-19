import mattersend
from pyfakefs import fake_filesystem_unittest


class PayloadTest(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.CreateFile('/etc/mattersend.conf', contents='''[DEFAULT]
url=https://chat.mydomain.com/hooks/abcdefghi123456

[angrybot]
icon = :angry:
username = AngryBot''')
        self.fs.CreateFile('/etc/mime.types', contents='text/x-diff diff')
        self.fs.CreateFile('/home/test/source.coffee')
        self.fs.CreateFile('/home/test/source.diff')
        self.fs.CreateFile('/home/test/Makefile')

    def test_simple_1(self):
        payload = mattersend.send(channel='town_square',
                                  message='test message',
                                  just_return=True)

        self.assertEqual(payload, r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town_square",
    "text": "test message"
}""")

    def test_section(self):
        payload = mattersend.send(channel='town_square',
                                  message='test message',
                                  config_section='angrybot',
                                  just_return=True)

        self.assertEqual(payload, r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town_square",
    "icon_url": "https://chat.mydomain.com/static/images/emoji/angry.png",
    "text": "test message",
    "username": "AngryBot"
}""")

    def test_override_url(self):
        payload = mattersend.send(channel='town_square',
                                  message='test message',
                                  url='http://chat.net/hooks/abdegh12',
                                  just_return=True)

        self.assertEqual(payload, r"""POST http://chat.net/hooks/abdegh12
{
    "channel": "town_square",
    "text": "test message"
}""")

    def test_syntax_by_ext(self):
        payload = mattersend.send(channel='town_square',
                                  filename='/home/test/source.coffee',
                                  just_return=True)

        self.assertEqual(payload, r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town_square",
    "text": "```coffeescript\n```"
}""")

    def test_syntax_by_mime(self):
        payload = mattersend.send(channel='town_square',
                                  filename='/home/test/source.diff',
                                  just_return=True)

        self.assertEqual(payload, r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town_square",
    "text": "```diff\n```"
}""")

    def test_syntax_mk(self):
        payload = mattersend.send(channel='town_square',
                                  filename='/home/test/Makefile',
                                  just_return=True)

        self.assertEqual(payload, r"""POST https://chat.mydomain.com/hooks/abcdefghi123456
{
    "channel": "town_square",
    "text": "```makefile\n```"
}""")
