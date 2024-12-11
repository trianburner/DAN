from sx126x.sx1262 import SX1262
from sx126x._sx126x import ERROR
from DANPacket import *
import time

sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
sx.begin(freq=923, bw=125.0, sf=8, cr=5, syncWord=0x12, power=22, preambleLength=8,
            implicit=False, implicitLen=0xFF, crcOn=True, txIq=False, rxIq=False,
            tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

print("Ready...")

while True:
    msg = input()
    #sx.send(msg.encode())
    sx.send(b'\x00\x00\x01\x00\x04{"username": "Chello", "type": "message", "text": "Check one two"}')
