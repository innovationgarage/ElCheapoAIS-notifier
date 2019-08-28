import threading
import time
import math

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
        if isinstance(signal, tuple):
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

g = SignalGenerator()
g.add_destination("green", "/sys/class/leds/orangepi:green:pwr/brightness")
g.add_destination("red", "/sys/class/leds/orangepi:red:status/brightness")
#g.add_destination("red", print_destination("red"))
#g.add_destination("green", print_destination("green"))
g.start()

g["red"] = (10, 0)
g["green"] = (5, 0)
time.sleep(3)
g["red"] = (0, 0)
