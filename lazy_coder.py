import sys

from bs4 import BeautifulSoup
import requests
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor


class MyBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel, self.factory.channel_key)
        print "Signed on as {}.".format(self.nickname)

    def joined(self, channel):
        print "Joined %s." % channel

    def privmsg(self, user, channel, msg):
        """
        Whenever someone says "why" give a lazy programmer response
        """
        if 'why' in msg.lower():
            # get lazy response
            because = self._get_because()

            # post message
            self.msg(self.factory.channel, because)

    def _get_because(self):
        req = requests.get('http://developerexcuses.com/')
        soup = BeautifulSoup(req.text)
        elem = soup.find('a')
        return elem.text.encode('ascii', 'ignore')


class MyBotFactory(protocol.ClientFactory):
    protocol = MyBot

    def __init__(self, nickname, channel, channel_key=None):
        self.nickname = nickname
        self.channel = channel
        self.channel_key = channel_key

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % reason

if __name__ == "__main__":
    try:
        nick = sys.argv[1]
        channel = sys.argv[2]
        chan_key = None
        if len(sys.argv) == 4:
            chan_key = sys.argv[3]
        reactor.connectTCP('irc.freenode.net', 6667, MyBotFactory(
            nickname=nick, channel=channel, channel_key=chan_key))
        reactor.run()
    except IndexError:
        print "Please specify a nickname & channel name."
        print "Example:"
        print "    python {} nick channel [channel_password]"\
            .format(sys.argv[0])
