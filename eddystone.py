### the code is adapted/taken from https://github.com/forksociety/PyBeacon/tree/master/PyBeacon

import subprocess
import argparse
from enum import Enum


# The default url
defaultUrl = "https://goo.gl/SkcDTN"

# The default uid
defaultUid = "01234567890123456789012345678901"

DEVNULL=subprocess.DEVNULL

schemes = [
        "http://www.",
        "https://www.",
        "http://",
        "https://",
        ]


class Eddystone(Enum):
    """Enumerator for Eddystone URL."""

    uid = 0x00
    url = 0x10
    eid = 0x30

extensions = [
        ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
        ".com", ".org", ".edu", ".net", ".info", ".biz", ".gov",
        ]

def encodeurl(url):
    """URL Encoder."""
    i = 0
    data = []
    ### data will store the index of schemes
    for s in range(len(schemes)):
        scheme = schemes[s]
        if url.startswith(scheme):
            data.append(s)
            i += len(scheme)
            break
    else:
        raise Exception("Invalid url scheme")

    while i < len(url):
        if url[i] == '.':
            for e in range(len(extensions)):
                expansion = extensions[e]
                ## check for extensions
                if url.startswith(expansion, i):
                    ### e is the index in extensions
                    data.append(e)

                    i += len(expansion)
                    break
            else:
                data.append(0x2E)
                i += 1
        else:
            ### converts the character into ASCII
            data.append(ord(url[i]))
            i += 1

    return data

def encodeUid(uid):
    """UID Encoder."""
    ## length of UID should be 32 and it should be in hex
    if not uidIsValid(uid):
        raise ValueError("Invalid uid. Please specify a valid 16-byte (e.g 32 hex digits) hex string")
    ret = []
    ## ret return the 16 byte address [2 hex digits makes a byte]
    for i in range(0, len(uid), 2):
        ret.append(int(uid[i:i+2], 16))
    ## byte 18 and byte 19 should be 0 according to eddystone standards
    ret.append(0x00)
    ret.append(0x00)
    return ret

def encodeEid(eid):
   if not eidIsValid(eid):
      raise ValueError("Invalid eid")
   ret=[]
   for i in range (0,len(eid),2):
      ret.append(int(eid[i:i+2],16))

   return ret       



def eidIsValid(eid):
   if len(eid) == 16:
     try:
       int (eid,16)
       return True
     except ValueError:
       return False
   else:
     return False
  
def uidIsValid(uid):
    """UID Validation."""
    if len(uid) == 32:
        try:
            ### converts the hex uid in decimal
            int(uid, 16)
            return True
        except ValueError:
            return False
    else:
        return False


def encodeMessage(data, beacon_type):
    """Message encoder."""
    if beacon_type == Eddystone.url:
        payload = encodeurl(data)

    elif beacon_type == Eddystone.eid:
         payload = encodeEid(data)

    elif beacon_type == Eddystone.uid:
        payload = encodeUid(data)
    encodedmessageLength = len(payload)


    ## encode-UID will be 18 Bytes long
    if encodedmessageLength > 18:
        raise Exception("Encoded url too long (max 18 bytes)")
   ##https://github.com/google/eddystone/blob/master/protocol-specification.md
    message = [
            0x02,   # Flags length
            0x01,   # Flags data type value
            0x1a,   # Flags data

            0x03,   # Service UUID length
            0x03,   # Service UUID data type value
            0xaa,   # 16-bit Eddystone UUID
            0xfe,   # 16-bit Eddystone UUID

            5 + len(payload),  # Service Data length
            0x16,   # Service Data data type value
            0xaa,   # 16-bit Eddystone UUID
            0xfe,   # 16-bit Eddystone UUID

            beacon_type.value,   # Eddystone-url frame type
            0xed,   # txpower
            ]

    message += payload

    return message

def stopAdvertising():
    """Stop advertising."""
    print("Stopping advertising")
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 00",
                    shell=True, stdout=DEVNULL)

def advertise(ad, beacon_type):
    """Advertise an eddystone URL."""
    print("Advertising: {} : {}".format(beacon_type.name, ad))
    message = encodeMessage(ad, beacon_type)

    # Prepend the length of the whole message
    message.insert(0, len(message))

    # Pad message to 32 bytes for hcitool
    while len(message) < 32:
        message.append(0x00)

    # Make a list of hex strings from the list of numbers
    message = map(lambda x: "%02x" % x, message)

    # Concatenate all the hex strings, separated by spaces
    message = " ".join(message)


    subprocess.call("sudo hciconfig hci0 up",
                    shell=True, stdout=DEVNULL)

    # Stop advertising
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 00",
                    shell=True, stdout=DEVNULL)

    # Set message
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 " + message,
                    shell=True, stdout=DEVNULL)

    # Resume advertising
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 01",
                    shell=True, stdout=DEVNULL)


parser = argparse.ArgumentParser(description='eddystone script')


parser.add_argument('--uid', dest='uid', type=str, nargs='?',default=defaultUid,help='eddystone uid')
parser.add_argument('--url', dest='url', type=str, nargs='?', help='eddystone URL')
parser.add_argument('-t', '--terminate', action='store_true',help='Stop advertising URL.')
parser.add_argument('--eid',dest='eid',type=str,help='advertise EID')

args=parser.parse_args()

if __name__ == "__main__":
    subprocess.call(["sudo", "-v"])
    if args.terminate:
        stopAdvertising()
    elif args.url:
        advertise(args.url,Eddystone.url)
    elif args.eid:
        advertise(args.eid,Eddystone.eid)
    else:
        advertise(args.uid,Eddystone.uid)
