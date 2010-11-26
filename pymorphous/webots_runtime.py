""" !!!!! This is pseudocode for the webots runtime  !!!!! """

import time
import webots
import uuid
import pymporphous.common #Field

class Message(object):
    def __init__(self, id, time, data):
        self.id = id
        self.time = time
        self._data = data
        
class WebotsDevice(object):
    def __init__(self):
        self.id = uuid()
        self._fields = {} # dict of fields
        self._new_fields = {} # dict of fields
        self._data = {} # dict of values
        self.time = time.time()
        self._nbrs = {} # map neighbor to time
        webots.register_incoming_message(self.receive_message)
        
    def receive_message(self, message):
        #This is within a signal handler, so no interrupts 
        self._nbrs[message.id] = message.time
        for (b, v) in message.data.items():
            if not hasattr(self._new_fields, b):
                self._new_fields[b] = Field()
            self._new_fields[b][message.id] = value

    def nbr(self, value, extra_key=None):
        b = big_backtrace_statement()
        if extra_key:
            self._nbr("%s%s" % (b, extra_key), value)
        else:
            self._nbr(b, value)
            
    def _nbr(self, b, value):        
        if hasattr(self._data, b):
            raise Exception("Runtime exception in nbr")
        self._data[b] = value
        return getattr(self._fields, b, Field())
    
    def _step(self):
        self.step()
        self.time = time.time()
        for n in self._nbrs:
            webots.send_message(Message(self.id, self.time, self._data))
        self._data = {}
        # time out old nbrs and field values
        for (n, t) in self._nbrs.items():
            if t + TIMEOUT < self.time:
                del self._nbrs[n]
        for (b, f) in self._fields.items():
            for (id, v) in f.items():
                if not hasattr(self._nbrs, id):
                    del f[id]
        for (b,f) in self._fields.items():
            if len(f) == 0:
                del self._fields[b]

        # bring in the new field values
        webots.disable_interrupts()
        for (b,f) in self._new_fields.items():
            if not hasattr(self._fields, b):
                self._fields[b] = f
            else:
                for (id, v) in f.items():
                    self._fields[id] = v
        webots.enable_interrupts()
