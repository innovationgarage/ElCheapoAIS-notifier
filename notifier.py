import threading
import time
import math
import select
import os.path
import sys
import json

def item_signal(frequency, phase=0):
    i = 0
    while True:
        yield int(math.floor(2 * (i * frequency + phase)) % 2 == 0)
        i += 1

def test(signal, length=20):
    for i, v in enumerate(signal):
        if i > length:
            break
        print(i, v)

def file_destination(filename):
    def destination(value):
        with open(filename, 'wb') as f:
            f.write(str(value).encode("utf-8"))
    return destination

def print_destination(name):
    def destination(value):
        print("%s=%s" % (name, value))
    return destination

class SignalGenerator(threading.Thread):
    def __init__(self, *arg, **kw):
        threading.Thread.__init__(self, *arg, **kw)
        self.timestep = 0.001
        self.signals = {}
        self.destinations = {}
        self.lastvals = {}
        
    def run(self, *arg, **kw):
        while True:
            time.sleep(self.timestep)
            for destination, item in self.signals.items():
                value = next(item)
                if value != self.lastvals.get(destination, None):
                    self.lastvals[destination] = value
                    if destination in self.destinations:
                        self.destinations[destination](value)

    def add_destination(self, name, destination):
        if isinstance(destination, str):
            destination = file_destination(destination)
        self.destinations[name] = destination

    def __setitem__(self, name, signal):
        if isinstance(signal, (tuple, list)):
            frequency = self.timestep * signal[0]
            phase = 0
            if signal[1:]:
                phase = signal[1]
            signal = item_signal(frequency, phase)
        self.signals[name] = signal

    def __delitem__(self, name):
        del self.signals[name]

    def __getitem__(self, name):
        return self.signals[name]

class Notifier(object):
    def __init__(self, source, destinations, mappings):
        self.source = source
        self.destinations = destinations
        self.mappings = mappings
        
        self.values = {}

        if not os.path.exists(source):
            os.mkfifo(source)
        
        self.signalgen = SignalGenerator()
        self.signalgen.daemon = True
        self.signalgen.start()

        for name, dest in destinations.items():
            self.signalgen.add_destination(name, dest)

        self.map()
        
        self.waitforinput()
            
    def waitforinput(self):
        while True:
            print("Opening pipe")
            with open(self.source, 'r') as f:
                for line in f:
                    name, value = line.split("=")
                    self.values[name] = int(value)
                    self.map()

    def match(self, rule):
        for name, value in rule.items():
            if self.values.get(name, 0) < value:
                return False
        return True
            
    def map(self):
        print("Matching %s" % (self.values,))
        for rule in self.mappings:
            if self.match(rule["in"]):
                print("    Matching rule: %s" % (rule,))
                for name, value in rule["out"].items():
                    self.signalgen[name] = value
                return
        print("    No matching rule")

def signalgentest():
    g = SignalGenerator()
    g.daemon = True
    g.add_destination("red", print_destination("red"))
    g.add_destination("green", print_destination("green"))
    g.start()
    return g
        
if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        config = json.load(f)
    Notifier(**config)
