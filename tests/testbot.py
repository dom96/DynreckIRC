#!/usr/bin/env python
import sys, os.path
sys.path.append("..")
from src import IRC

def privmsg(server, word, word_eol, args):
  if word[3] == "|lag":
    server.send("PRIVMSG %s :Lag is %s" % (word[2], server.pinger.lag))


print "DynreckIRC " + IRC.version
# Initialize a server instance
s = IRC.connection(["irc.freenode.net", 6667, "", False], \
    ['DynreckBot', 'DynreckBot1', 'DynreckBot2'], "Dynreck", "Dynreck")
s.autojoinchans = ["#()"]

s.events.hook_event("PRIVMSG", privmsg)

s.connect(pingServ=True, threaded=False)
