#!/usr/bin/env python
"""
DynreckIRC
Copyright (C) 2010 dom96
"""
import logger
import thread
########################
# IRC Library info     #
########################
version = "0.1"

class connection:
    def __init__(self, addrInfo, nicks, realname, username):
        self.addrInfo = addrInfo # [address - str, port - int, PASS - str, ssl - bool]
        self.nicks = nicks # Nicks to use
        self.realname = realname # Your realname
        self.username = username # Your username
        
        # The following three variables are None, if not connected to a server
        self.address = None # Address of the server, if connected
        self.port = None # port, if connected
        self.socket = None # this servers socket object, if connected
        
        self.autojoinchans = [] # These will be joined when the 001 command is received.
        
        self.nick = nicks[0]
        
        # Each server has it's own events
        import events
        self.events = events.events_manager()
        # And also the serverEvents, stuff like, when you get disconnected etc.
        self.serverEvents = events.events_manager()
        
        # pinger
        self.pinger = self.server_pinger(self)
        
        self.gen_eol = gen_eol
        
    def connect(self, pingServ=True, threaded=True):
        """
        Connects to this server, if pingServ is True lag will be measured by pinging the server.
        If threaded is True, connect will be executed in a new thread.
        """
        try:
            # If connect is called, spawn it in a new thread
            if threaded == True:
                thread.start_new(self.connect, (pingServ, False))
                return
            
            import socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # SSL
            if self.addrInfo[3] == True:
                try:
                    import ssl
                    self.socket = ssl.wrap_socket(socket)
                except:
                    logger.log_instance.log("SSL ERROR", "IRC.server.connect", "error")
                
                
            # Connect to the server
            try:
                self.socket.connect((self.addrInfo[0], self.addrInfo[1]))
                self.address = self.addrInfo[0]
                self.port = self.addrInfo[1]
            except Exception as err:
                self.address = None
                self.port = None
                self.socket = None
                self.serverEvents.call_events(self, "connect_error", ["connect_error", err], [])
                
                logger.log_instance.log("Couldn't connect to server: " + str(err), "IRC.server.connect", "error")
                
            
            # Register the connection - Send (PASS) NICK, USER.
            if self.addrInfo[2] != '':
                self.socket.send("PASS %s \r\n" % (self.addrInfo[2]))
            
            self.socket.send("NICK %s\r\n" % (self.nick))
            
            self.socket.send("USER %s %s %s :%s\r\n" % (self.username, \
                self.username, self.addrInfo[0], self.realname))
            
            # Hook the RPL_WELCOME(001) command, to the ping_server function.
            if pingServ:
                self.events.hook_event("001", lambda s, w, w_eol, \
                    args: thread.start_new(lambda x: self.pinger.ping_server(), (None,)))
                    
            # And also hook the 001 to the autojoin_chans function
            if len(self.autojoinchans) != 0:
                self.events.hook_event("001", lambda s, w, w_eol, \
                    args: thread.start_new(lambda x: self.autojoin_chans(), (None,)))
                    
            # This will reply to the PING command
            self.events.hook_event("PING", lambda serv, w, w_eol, args: serv.send("PONG %s" % (w_eol[2])), 5)
            
            #########################
            # RESPONSE FUNCTION     #
            #########################
            self.response() # Use this thread for the response function.

        except Exception as err:
            import traceback
            traceback.print_exc()
        
            logger.log_instance.log(err, "IRC.connect", "critical")
        
    def response(self):
        msg = ""
        while self.address != None:
            msg += self.socket.recv(1024)
            if msg != "":
                if msg.endswith('\r\n'):
                    logger.log_instance.log(msg, "IRC.server", "info")
                    for m in msg.split("\r\n"):
                        if m != "":
                            # If the message does not start with a :
                            # Prepend ":Server.address.here"
                            if m.startswith(":") != True:
                                m = ":" + self.address + " " + m
                        
                            ###############################
                            # Splits the message properly #
                            ###############################
                            if ":" in m[1:]: # Check if there is a : in this command(Excluding the first character, which usually is a :)
                                # Gets everything after : as one instead of split into spaces
                                n_front_colon = m
                                if n_front_colon.startswith(":"):
                                    n_front_colon = n_front_colon[1:]
                                bef_colon, aft_colon = (n_front_colon.split(":")[0], ":".join(n_front_colon.split(":")[1:]))
                                
                                word = bef_colon.split()
                                word.append(aft_colon)
                            
                                word_eol = gen_eol(bef_colon, aft_colon)
                            else:
                                word = m[1:].split()
                                word_eol = gen_eol(m)

                            self.events.call_events(self, word[1], word, word_eol)
                            
                    msg = ""
            else:
                # msg is equal to '' which means the server sent ''
                # Which means the server disconnected us
                self.serverEvents.call_events(self, "disconnect", ["disconnect", "Server closed connection"], [])
                self.address = None
                self.port = None
                self.socket = None
                return
                            
    def send(self, text):
        self.socket.send(text + "\r\n")
        logger.log_instance.log(text + "\\r\\n", "IRC.server.send", "info")
    
    class server_pinger:
        def __init__(self, server):
            self.server = server
            self.lag = 0
    
        def ping_server(self):
            self.server.events.hook_event("PONG", self.pong_event)
            import time
            while self.server.address != None:
                time.sleep(10)
                self.server.send("PING :LAG%s" % (time.time()))
                
        def pong_event(self, server, word, word_eol, args):
            import time
            diffTime = time.time() - float(word[3].replace("LAG", ""))
            self.lag = diffTime
            self.server.serverEvents.call_events(self, "lag_changed", ["lag_changed", diffTime], [])
            
            #logger.log_instance.log(diffTime, "IRC.server_pinger.pong_event", "debug")
            
    def autojoin_chans(self):
        for chan in self.autojoinchans:
            self.send("JOIN %s" % (chan))
            
    class channel:
        def __init__(self, name):
            self.name = name
            self.mode = ""
            self.topic = ""
            self.userManager = self.user_manager(self.name)
            
            
        class user_manager:
            def __init__(self, channel):
                self.users = []
                self.channel = channel
            
            def names_event(self, server, word, word_eol, args):
                pass
                # TODO: Get the users on the channel and other info. Update them too.
            
            
            class user:
                def __init__(self, nick, mode=""):
                    self.nick = nick
                    self.mode = mode
                    self.realname = ""
                    self.username = ""
                    self.hostname = ""

            
def gen_eol(text, aft_colon=""):
    word_eol = []
    split = text.split()
    
    if aft_colon != "":
        split.append(aft_colon)
    
    split.reverse()
    for i in range(len(split)):
        value = split[:len(split) - i]
        value.reverse()
        word_eol.append(" ".join(value))
    return word_eol
    
    
    
    
