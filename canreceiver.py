#!/usr/bin/env python3
##############################################################################
#
#    SkyLines Tracker is a location tracking client for the SkyLines platform <www.skylines-project.org>.
#    Copyright (C) 2019  Andreas Lüthi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import argparse
import socket
import struct

import can
from skylines import create_fix_message
from collections import deque

parser = argparse.ArgumentParser(description='Read position updates from can-bus and sent it to SkyLines')
parser.add_argument('trackingkey', metavar='key', type=lambda x: int(x, 16), help='Your live tracking key')
parser.add_argument('-interval', metavar='interval', type=int, default=5,
                    help='Tracking interval in seconds, default=5')
parser.add_argument('-channel', metavar='channel', type=str, default='vcan0', help='Canbus, default=can0')
args = parser.parse_args()
tracking_key = args.trackingkey
tracking_interval = args.interval
channel = args.channel

CAN_SFF_MASK = 0x000007FF
HOST_PORT = ("skylines.aero", 5597)

bus = can.interface.Bus(channel=channel, bustype='socketcan')
bus.set_filters(
    [{"can_id": 316, "can_mask": CAN_SFF_MASK},
     {"can_id": 322, "can_mask": CAN_SFF_MASK},
     {"can_id": 354, "can_mask": CAN_SFF_MASK},
     {"can_id": 1036, "can_mask": CAN_SFF_MASK},
     {"can_id": 1037, "can_mask": CAN_SFF_MASK},
     {"can_id": 1039, "can_mask": CAN_SFF_MASK},
     {"can_id": 1040, "can_mask": CAN_SFF_MASK},
     {"can_id": 1200, "can_mask": CAN_SFF_MASK},
     {"can_id": 1506, "can_mask": CAN_SFF_MASK}])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP


def getFloat():
    return struct.unpack('>f', canMsg.data[4:8])[0]


def getDoubleL():
    return struct.unpack('>l', canMsg.data[4:8])[0] / 1E7


def getUshort():
    return struct.unpack('>H', canMsg.data[4:6])[0]


def getChar4():
    return struct.unpack('4b', canMsg.data[4:])


last_s = 0


def initParams():
    global lat, lon, gs, tt, tas, alt, vario, enl
    lat = None
    lon = None
    gs = None
    tt = None
    tas = None
    alt = None
    vario = None
    enl = None


initParams()

### skylinesMsgQueue = deque([])

for canMsg in bus:

    if canMsg.arbitration_id == 1200:  # UTC
        utc = getChar4()
        now_s = (utc[0] * 3600) + (utc[1] * 60) + utc[2]
        if now_s >= last_s + tracking_interval:
            last_s = now_s
            skylinesMsg = create_fix_message(
                tracking_key,
                now_s * 1000,
                latitude=lat,
                longitude=lon,
                track=tt,
                ground_speed=gs,
                airspeed=tas,
                altitude=alt,
                vario=vario,
                enl=enl)
            sock.sendto(skylinesMsg, (HOST_PORT[0], HOST_PORT[1]))
            initParams()
            ### skylinesMsgQueue.append(skylinesMsg)
            ### if 1000 < len(skylinesMsgQueue): skylinesMsgQueue.popleft()

    elif canMsg.arbitration_id == 316:
        tas = getFloat()

    elif canMsg.arbitration_id == 322:
        alt = getFloat()

    elif canMsg.arbitration_id == 354:
        vario = getFloat()

    elif canMsg.arbitration_id == 1036:
        lat = getDoubleL()

    elif canMsg.arbitration_id == 1037:
        lon = getDoubleL()

    elif canMsg.arbitration_id == 1039:
        gs = getFloat()

    elif canMsg.arbitration_id == 1040:
        tt = getFloat()

    elif canMsg.arbitration_id == 1506:
        enl = getUshort()

    else:
        print(canMsg.arbitration_id, canMsg.data)
