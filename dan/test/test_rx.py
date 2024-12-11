from sx126x.sx1262 import SX1262
from sx126x._sx126x import ERROR
from DANPacket import *
import time

def cb(events):
    if events & SX1262.RX_DONE:
        msg, err = sx.recv()
        error = SX1262.STATUS[err]
        print(">> ", DANPacket.decode(msg))
        if err: print("RECEIVE ERROR >> ", ERROR[err])

sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
sx.begin(freq=923, bw=125.0, sf=8, cr=5, syncWord=0x12, power=22, preambleLength=8,
            implicit=False, implicitLen=0xFF, crcOn=True, txIq=False, rxIq=False,
            tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

sx.setBlockingCallback(False, cb)

print("Listening...")

