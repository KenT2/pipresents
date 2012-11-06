import time

"""
6/11/2012 - first issue
"""

class StopWatch:

    def __init__(self):
        self.enable=False

    def on(self):
        self.enable=True

    def off(self):
        self.enable=False
    
    def start(self):
        if self.enable: self.sstart=time.clock()

    def split(self,text):
        if self.enable:
            self.end=time.clock()
            print text + " " + str(self.end-self.sstart) + " secs"
            self.sstart=time.clock()
        
    def stop(self,text):
        if self.enable:
            self.end=time.clock()
            print text + " " + str(self.end-self.sstart) + " secs"


class Monitor:
    def __init__(self):
        self.enable=False
        self.sstart=time.time()

    def on(self):
        self.enable=True
        
    def off(self):
        self.enable=False

    def log(self,text):
        if self.enable: print "%.2f" % (time.time()-self.sstart), " ", text
