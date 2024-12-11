from sx126x.sx1262 import SX1262
from sx126x._sx126x import ERROR
from DANPacket import *
import asyncio

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
    
def initialize_backend(func):
    global g_sx
    global g_packet_history
    global g_sx
    global g_packet
    global g_packet_count
    global g_message
    global g_callback
    global lock
    
    lock = asyncio.Lock()
    g_callback = func
    
    g_packet = None
    g_packet_count = 0
    g_packet_history = PacketCircularBuffer()
    g_sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)
    g_message = None

    # LoRa
    g_sx.begin(freq=923, bw=125.0, sf=8, cr=5, syncWord=0x12, power=22, preambleLength=8,
            implicit=False, implicitLen=0xFF, crcOn=True, txIq=False, rxIq=False,
            tcxoVoltage=1.7, useRegulatorLDO=False)

    g_sx.setBlockingCallback(False, callback)
    
def callback(events):
    if events & SX1262.RX_DONE:
        msg, err = g_sx.recv()
        if err != 0:
            print("RECEIVE ERROR >> ", ERROR[err])
        else:
            print("Packet received, msg: ", msg)
            packet = DANPacket.decode(msg)
            asyncio.get_event_loop().run_until_complete(g_callback(packet.content))
            
            # Re-transmit packet if not recently received
            if not g_packet_history.contains(packet):
                g_packet_history.write(packet)
                _sendPacket(g_sx, packet)
                
    elif events & SX1262.TX_DONE:
        print("Packet sent")
        lock.release()
    
async def _sendPacket(sx, packet):
    await lock.acquire()
    asyncio.sleep(1)
    packet_length, err = sx.send(packet)
    
    if err != 0:
        lock.release()
        print("SEND ERROR >> ", ERROR[err])

async def send(content):
    global g_sx
    global g_packet
    global g_packet_count
    
    # TBI: Implement for other types of packet.
    # TBI: Chop content into multiple packets.
    
    g_packet_count = (g_packet_count + 1) % DAN_NODE_PACKET_MAX_ID
    
    g_packet = BroadcastPacket(DAN_NODE_ID, g_packet_count, content).encode()
    print("Made packet >> ", g_packet)
    
    await _sendPacket(g_sx, g_packet)