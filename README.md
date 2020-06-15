# eddystone-protocol
using python to implement eddystone UID URL and EID

## Requirements
The script works with linux and requires bluez linux package

## Eddystone EID
Eddystone EID is a security protocol for Eddystone UID. This safeguards the UID broadcasted by the beacon from unauthorised clients/recievers. Only trusted clients can resolve the advertised UID. To use EIDs, Beacons need to be registered. Then, if EIDs are enabled, beacons will not broadcast their real Namespace and Instance values. Instead, they will transmit seemingly random IDs, changing them on regular intervals
