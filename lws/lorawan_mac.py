# TODO: this file includes the MAC implementation of the LoRaWAN specification. As this is only intended for high level simulation/tutorial purposes(for understanding the behaviorus of the MAC layer etc.), the consequence of a MAC command will be abstract to the manipulation of some data structure e.g. for a dict: device_status.update({tx_pow : new_tx_pow}) etc.

# Also, this can be used further down the line to test different Adaptive Data Rate (ADR) algorithms

# There exists 8 different MAC message types:
# 000 -> Join-request
# 001 -> Join-accept
# 010 -> Unconfirmed Data Up
# 011 -> Unconfirmed Data Down
# 100 -> Confirmed Data Up
# 101 -> Confirmed Data Down
# 110 -> Rejoin-request
# 111 -> Proprietary

# Confirmed data message must be ACKed by the receiver
from enum import Enum

MAC_MSG_TYPES = {
    "JOIN_REQ": 0b000,
    "JOIN_ACC": 0b001,
    "UNCON_DATA_UP": 0b010,
    "UNCON_DATA_DOWN": 0b011,
    "CON_DATA_UP": 0b100,
    "CON_DATA_DOWN": 0b101,
    "REJOIN_REQ": 0b110,
    "PROPRIETARY": 0b111,
}


class MACCommand():
    @property
    def bin_payload(self):
        # concatnate all the fields into the PHYPayload
        return


class EndDeviceMACLayer():

    def parse_mac_command(self, mac_cmd):
        pass

    def execute_mac_command(self):
        pass

    def generate_mac_response(self):
        return


class LoRaWANServerMACLayer():
    pass


if __name__ == "__main__":
    e_m = EndDeviceMACLayer()
    print(MAC_MSG_TYPES["PROPRIETARY"])
