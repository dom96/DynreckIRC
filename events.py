#!/usr/bin/env python
"""
MDS IRC Lib
Copyright (C) 2009 Mad Dog Software 
http://maddogsoftware.co.uk - morfeusz8@yahoo.co.uk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""
import logger
import threading
lock = threading.Lock() #The global lock for events_manager.events

class events_manager:
    def __init__(self):
        self.events = []
        
    def __str__(self):
        formatted_string = ""
        for i in self.events:
            formatted_string += "[" + i.command + "]"
            
        return formatted_string
        
        
    def hook_event(self, command, callback, priority=0, args=[]):
        import uuid
        id = uuid.uuid1()
        e = self.event(command, callback, priority, str(id), args)
        self.events.append(e)
        logger.log_instance.log("Added event, %s, with ID %s" % (command, id), "events.hook_event")
        
        return str(id)
        
    def unhook_event(self, id):
        global lock
        with lock: #Only take the lock when using the events list
            for e in self.events:
                if e.id == id:
                    self.events.remove(e)
                    return True
                
        return False
        
    def call_events(self, server, command, word, word_eol):
        global lock
        with lock: #Only take the lock when using the events list
            sortedList = self.events
            
        sortedList.sort(cmp=lambda x, y: cmp(x.priority, y.priority))    
        for e in sortedList:
            if e.command.lower() == command.lower():
                try:
                    e.callback(server, word, word_eol, e.args)
                except Exception as err:
                    logger.log_instance.log("An error occured calling an event, the callback might be improperly formed," \
                       + " server = %s Command = %s, callback = %s, error = %s" \
                          % (server.address, e.command, e.callback, str(err)), "events.call_events", "error")
        
    class event:
        def __init__(self, command, callback, priority, id, args):
            self.command = command
            self.callback = callback
            self.priority = priority
            self.id = id
            self.args = args
        
