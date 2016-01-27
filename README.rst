mattersend
==========

CLI tool to send messages to the Incoming webhook of mattermost (http://www.mattermost.org/).

Help
----

::

	usage: mattersend [-h] [-V] [-C CONFIG] [-s SECTION] [-c CHANNEL] [-U URL]
	                  [-u USERNAME] [-i ICON]
	                  [message]

	Sends messages to mattermost's incoming webhooks via CLI

	positional arguments:
	  message               The message to send or the attachment content if the
	                        -a argument is specified. If not specified it will be
	                        read from STDIN

	optional arguments:
	  -h, --help            show this help message and exit
	  -V, --version         show program's version number and exit
	  -C CONFIG, --config CONFIG
	                        Use a different configuration file
	  -s SECTION, --section SECTION
	                        Configuration file section
	  -c CHANNEL, --channel CHANNEL
	                        Send to this channel or @username
	  -U URL, --url URL     Mattermost webhook URL
	  -u USERNAME, --username USERNAME
	                        Username
	  -i ICON, --icon ICON  Icon

Configuration file
------------------

The only required option to start sending messages to mattermost is the webhook url.
You can either set this in a configurations file (globally in */etc/mattersend.conf* or locally in *$HOME/.mattersend.conf*) or specify it on the CLI with the --url argument.

You can have multiple sections to override DEFAULT settings and later select them from the CLI with the --section argument.

This is an example of a configuration file for mattersend::

	[DEFAULT]
	url = https://mattermost.example.com/hooks/XXXXXXXXXXXXXXXXXXXXXXX
	icon = :ghost:
	username = This is a bot
	channel = @myself

	[angrybot]
	icon = :angry:
	username = AngryBot

Example usage
-------------

::

	echo "Hello world!" | mattersend -U https://mattermost.example.com/hooks/XXX
	mattersend -U https://mattermost.example.com/hooks/XXX "Hello world!"

LICENSE
-------
Copyright (c) 2015 Massimiliano Torromeo

mattersend is free software released under the terms of the BSD license.

See the LICENSE file provided with the source distribution for full details.

Contacts
--------

* Massimiliano Torromeo <massimiliano.torromeo@gmail.com>
