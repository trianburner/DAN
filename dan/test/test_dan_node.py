from sx1262 import *
from _sx126x import *
from DANPacket import *


DAN_NODE_ID = 1
DAN_NODE_PACKET_CB_MAX_LENGTH = 20
DAN_NODE_PACKET_MAX_ID = 256


class PacketCircularBuffer:
    """
    Contains ids of sent packets.
    
    When a packet is received, we check if it is already handled. If not, we
    should propagate it, then process the message content.
    """
    def __init__(self, capacity=DAN_NODE_PACKET_CB_MAX_LENGTH):
        self._list = []
        self._size = 0
        self._ptr = 0
        self._capacity = capacity
    
    def write(self, packet):
        if self._size >= self._capacity:
            self[self._ptr] = packet
        else:
            self._list.append(packet)
            self._size += 1
        self._ptr = (self._ptr + 1) % self._capacity
            
    def contains(self, packet):
        for old_packet in self._list:
            if packet.same_header(old_packet):
                return True
        return False


def callback(events):
    if events & SX1262.RX_DONE:
        msg, err = sx.recv()
        if err == 0:
            onMessageReceived(msg)
    elif events & SX1262.TX_DONE:
        onMessageSent()


def onMessageReceived(msg):
    # TBI: Handle message content
    
    packet = DANPacket.decode(msg)
    if not packet_history.contains(packet):
        sendPacket(packet)


def onMessageSent():
    # Switch back to receiving data mode
    sx.startReceive()


def sendPacket(packet):
    sx.send(packet.encode())


def send(content: bytes):
    # TBI: Implement for other types of packet.
    # TBI: Chop content into multiple packets.
    
    if len(content) > DANPacket.MAXLENGTH:
        return
    
    packet = BroadcastPacket(DAN_NODE_ID, id, content)
    sendPacket(packet)
    packet_count = (packet_count + 1) % DAN_NODE_PACKET_MAX_ID


packet = None
packet_count = 0
packet_history = PacketCircularBuffer()
sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
sx.begin(freq=923, bw=125.0, sf=12, cr=8, syncWord=0x12,
         power=-5, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

sx.setBlockingCallback(False, callback)
