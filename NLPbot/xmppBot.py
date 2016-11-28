#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
import logging
import getpass
import pika
from optparse import OptionParser

from threading import Timer


import sleekxmpp
import schedule

from chatbot import chatbot

#from queue import Queue, Empty
from twisted.internet import task
from twisted.internet import reactor

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class EchoBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """


    def __init__(self, jid, password,room,nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.room = room
        self.nick = nick
        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)

        # The groupchat_message event is triggered whenever a message
        # stanza is received from any chat room. If you also also
        # register a handler for the 'message' event, MUC messages
        # will be processed by both handlers.
#        self.add_event_handler("groupchat_message", self.muc_message)

        # The groupchat_presence event is triggered whenever a
        # presence stanza is received from any chat room, including
        # any presences you send yourself. To limit event handling
        # to a single room, use the events muc::room@server::presence,
        # muc::room@server::got_online, or muc::room@server::got_offline.
 #       self.add_event_handler("muc::%s::got_online" % self.room,
  #                             self.muc_online)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        import MQTTbot

        MQTTbot.init_mqtt()

        self.send_presence()
        self.get_roster()
        self.plugin['xep_0045'].joinMUC("DETI@conference.ubuntu",
                                        "bot"
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        )
        #self.plugin['xep_0045'].joinMUC("test2@conference.andrelopes",
         #                               "bot"
                                        # If a room password is needed, use:
                                        # password=the_room_password,
          #                              )

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['type'] in ('chat', 'normal'):
            print(msg['body'])
            result = chatbot.run_bot(msg['body'])
            if "remindme" in result:
                #schedule.every(10).seconds.do(self.remindMe("quim","dar banho ao cao"))
                Timer(10, lambda:self.remindMe("quim","dar banho ao cao"), ()).start()
                msg.reply("Thanks for sending\n%(body)s" % msg).send()
            msg.reply("bot_reply: %(body)s" % msg).send()




    def remindMe(s,who,what):
        print ("Hey %s, just to remind you: %s" % (who,what))

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)




if __name__ == '__main__':
#    xmpp_queue = Queue()
    chatbot = chatbot()





    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
    optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = raw_input("Password: ")
    if opts.room is None:
        opts.room = raw_input("MUC room: ")

    if opts.nick is None:
        opts.nick = "chatbot"

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = EchoBot(opts.jid, opts.password,opts.room, opts.nick)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    xmpp.register_plugin('xep_0045')  # Multi-User Chat

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    import ssl
    xmpp.ssl_version = ssl.PROTOCOL_SSLv23

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect(('192.168.215.165', 5222)):
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...



        xmpp.process(block=True)
        schedule.run_pending()
        print("Done")

    else:
        print("Unable to connect.")

