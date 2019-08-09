import struct

from crc16pure import crc16xmodem

MAGIC = 0x5DF4B67B
TYPE_PING = 1
TYPE_ACK = 2
TYPE_FIX = 3
TYPE_TRAFFIC_REQUEST = 4
TYPE_TRAFFIC_RESPONSE = 5
TYPE_USER_NAME_REQUEST = 6
TYPE_USER_NAME_RESPONSE = 7

FLAG_ACK_BAD_KEY = 0x1

FLAG_LOCATION = 0x1
FLAG_TRACK = 0x2
FLAG_GROUND_SPEED = 0x4
FLAG_AIRSPEED = 0x8
FLAG_ALTITUDE = 0x10
FLAG_VARIO = 0x20
FLAG_ENL = 0x40


def calc_crc(data):
    assert len(data) >= 16

    crc = crc16xmodem(data[:4])
    crc = crc16xmodem(b"\0\0", crc)
    crc = crc16xmodem(data[6:], crc)
    return crc


def set_crc(data):
    assert len(data) >= 16

    crc = calc_crc(data)
    return data[:4] + struct.pack("!H", crc) + data[6:]


def create_fix_message(
        tracking_key,
        time,
        latitude=None,
        longitude=None,
        track=None,
        ground_speed=None,
        airspeed=None,
        altitude=None,
        vario=None,
        enl=None):
    flags = 0

    if latitude is None or longitude is None:
        latitude = 0
        longitude = 0
    else:
        latitude *= 1000000
        longitude *= 1000000
        flags |= FLAG_LOCATION

    if track is None:
        track = 0
    else:
        flags |= FLAG_TRACK

    if ground_speed is None:
        ground_speed = 0
    else:
        ground_speed *= 16
        flags |= FLAG_GROUND_SPEED

    if airspeed is None:
        airspeed = 0
    else:
        airspeed *= 16
        flags |= FLAG_AIRSPEED

    if altitude is None:
        altitude = 0
    else:
        flags |= FLAG_ALTITUDE

    if vario is None:
        vario = 0
    else:
        vario *= 256
        flags |= FLAG_VARIO

    if enl is None:
        enl = 0
    else:
        flags |= FLAG_ENL

    message = struct.pack(
        "!IHHQIIiiIHHHhhH",
        MAGIC,
        0,
        TYPE_FIX,
        tracking_key,
        flags,
        int(time),
        int(latitude),
        int(longitude),
        0,
        int(track),
        int(ground_speed),
        int(airspeed),
        int(altitude),
        int(vario),
        int(enl))
    return set_crc(message)
