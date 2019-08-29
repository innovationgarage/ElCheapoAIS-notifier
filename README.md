# ElCheapoAIS-notifier

## Usage

    python notifier.py config.json

## Protocol

The notifier opens a named pipe and reads commands from the pipe. The commands are each one line and on the form

    NAME=VALUe
    
where NAME is a string and value is an integer. The names available correspond to the names used in the "in" part of a rule
in the "mappings" ruleset in the config. Each command updates the value of the named parameter in an internal state and then
applies the mappings ruleset to that state.

## Configuration

The configuration consists of the pathname of the named pipe, a dictionary of outputs and a set of mapping rules.

The outputs map output names to sysfs control files for LED:s on your board. E.g.

    "destinations": {"green": "/sys/class/leds/orangepi:green:pwr/brightness",
                     "red": "/sys/class/leds/orangepi:red:status/brightness"},
                     
defines two outputs corresponding to the red and green leds on an OrangePI R1 under OpenWRT.

The mapping ruleset is a list traversed from top to bottom for each state change following an input command, with the outputs
of the first matching rule applied. A rule matches if for every key/value pair specified in its "in" section, the value is
smaller than or equal to the value of the same parameter in the current state. The outputs consists of a destination and
a tuple of [frequency, phase], where frequency is in Hz, and phase is a value between 0 and 1. The waveform starts with
outputting 1:s for halve the wavelength, then 0:s. This also means that [0, 0] will output a constant 1, while [0, 0.5] will
output a constant 0.

    "mappings": [{"in": {"nmea": 1, "manhole": 1, "geocloud": 1}, "out": {"red": [0, 0], "green": [0, 0]}},
                 {"in": {"nmea": 1, "manhole": 1, "geocloud": 0}, "out": {"red": [1, 0],   "green": [1, 0.5]}}]

if all the parameters nmea, manhole and geocloud are 1 or above, both red and green will be on. If geocloud is 0, the two
leds will blink - one of them being off when the other one is on and vice versa.
