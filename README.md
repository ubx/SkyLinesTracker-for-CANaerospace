# SkyLinesTracker-for-CANaerospace
SkyLines Tracker for a CANaerospace device is a simple tracking client for the SkyLines platform.
(very experimental!)
``````
./canreceiver.py -h
usage: canreceiver.py [-h] [-interval interval] [-channel channel] key

Read position updates from can-bus and sent it to SkyLines

positional arguments:
  key                 Your live tracking key

optional arguments:
  -h, --help          show this help message and exit
  -interval interval  Tracking interval in seconds, default=5
  -channel channel    Canbus, default=can0

``````