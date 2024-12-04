from sx1262 import *
# from _sx126x import *
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
    
    
def initialize_backend():
    global g_sx
    global g_packet_history
    global g_sx
    global g_packet
    global g_packet_count
    global g_message
    
    g_packet = None
    g_packet_count = 0
    g_packet_history = PacketCircularBuffer()
    g_sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)
    g_message = None

    # LoRa
    g_sx.begin(freq=923, bw=500.0, sf=12, cr=8, syncWord=0x12,
            power=-5, currentLimit=60.0, preambleLength=8,
            implicit=False, implicitLen=0xFF,
            crcOn=True, txIq=False, rxIq=False,
            tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

    g_sx.setBlockingCallback(False, callback)

    
def callback(events):
    global g_sx
    global g_packet_history
    if g_sx is None or g_packet_history is None:
        return
    
    if events & SX1262.RX_DONE:
        msg, err = g_sx.recv()
        if err == 0:
            _onMessageReceived(g_sx, msg)
    elif events & SX1262.TX_DONE:
        _onMessageSent(g_sx)


def _onMessageReceived(sx, msg, packet_history):
    global g_message
    # TBI: Handle message content
    packet = DANPacket.decode(msg)
    g_message = packet.contents
    if not packet_history.contains(packet):
        _sendPacket(sx, packet)


def _onMessageSent(sx):
    # Switch back to receiving data mode
    sx.startReceive()


def _sendPacket(sx, packet):
    sx.send(packet.encode())


def send(content: bytes):
    global g_sx
    global g_packet
    global g_packet_count
    if g_sx is None or g_packet is None or g_packet_count is None:
        return
    
    # TBI: Implement for other types of packet.
    # TBI: Chop content into multiple packets.
    
    if len(content) > DANPacket.MAXLENGTH:
        return
    
    g_packet = BroadcastPacket(DAN_NODE_ID, id, content)
    _sendPacket(g_sx, g_packet)
    g_packet_count = (g_packet_count + 1) % DAN_NODE_PACKET_MAX_ID

