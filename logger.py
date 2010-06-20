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
#I WAS GONNA USE THE LOGGING MODULE BUT DECIDED THAT IT IS 
#TOO COMPLICATED, AND MAKING A SIMPLE LOGGER MODULE IS EASIER.

import sys, os
import threading
lock = threading.Lock() #Lot's of threads call the log function
#They need to acquire the lock to do that

class logger:

    def __init__(self, text):
        """
        Starts the log, opens the file, writes text to the file, and a div tag
        """
        #FILENAME
        LOG_FILENAME = os.path.join(os.path.dirname(sys.argv[0]), "log.html")
        
        
        #Open the log file...
        self.fLog = open(LOG_FILENAME, "a")
        self.write("<div style=\"font-family:Calibri;\">\n" + text + "<br/>\n")


    def write(self, text):
        """
        Writes text to the log file
        """
        self.fLog.write(text)
        self.fLog.flush()
    
    def log(self, text, func, level="info"):
        """
        Formats and logs the text to file and prints it(Nicely :D)
        """
        try:
            global lock
            with lock:
                text = str(text).replace("\r", "")
                
                for i in range(len(text.split("\n"))):
                    if i == 0:
                        self.write(self.format(text.split("\n")[i], func, level))
         
                        print level + ":" + func + ":" + text.split("\n")[i]
                    else:
                        #Append to the log, without the level or func info, just write the message
                        self.write("%s<br/>" % (text.split("\n")[i]))
                        
                        indent = len(level + ":" + func + ":")
                        print " " * (indent - 1), text.split("\n")[i]

        except Exception as Err:
            print Err
        
    def format(self, text, func, level):
        """
        Formats the text into html
        """
        color = "RoyalBlue" #Default level color
        if level == "warning":
            color = "orange"
        elif level == "error":
            color = "OrangeRed"
        elif level == "critical":
            color = "red"
        elif level == "info":
            color = "black"
        elif level == "success":
            color = "LimeGreen"
        
        format_str = "<span style=\"color:%s;\">%s </span>\n" % (color, level)
        import datetime
        format_time = datetime.datetime.now().isoformat().replace("T", " ")
        
        format_str += "<span style=\"color:grey;\">%s </span>\n" % (format_time)
        format_str += "<span style=\"color:SlateBlue;\">%s </span>\n" % (func)
        format_str += "<span style=\"color:black;\">%s </span><br/>\n" % (text)
        
        return format_str
        
    def close(self, text):
        """
        Close the log file, and write the ending text to the file
        """
        self.fLog.write(text + "<br/>\n</div>\n")
        self.fLog.close()
    
#If this modules is imported, initialize the logger class
if __name__ != "__main__":
        log_instance = logger("MDSBot 0.1 initialized")
    
