
"""
    Defines Packet Types for our Network

    DANPacket: General superclass
    Broadcast: one to all
    DMPacket: one to one
    Multipacket: one to one split up into multiple (indexed by seq)
    PingPacket: check connectivity
    
    Getting data from a packet - Call DANPacket.decode(bytes). 
    Will return one of the packet types, whichever one was defined by the data


    Encoding data into a packet - Create one of the types, supplying the constructor with the necessary data.
    Then call .encode() to get a bytes object.
    
    """

class DANPacket:
    """These static vars should allow us to adjust the size of the packet elements without reprogramming everything"""
    SOURCEBYTES = 2
    DESTBYTES = 2
    IDBYTES = 2
    STRENCODING = 'utf-8'
    SEQBYTES = 1
    INFOBYTES = 1
    TYPEBITS = 2
    PADDING = 8 - TYPEBITS
    ENDIANNESS = 'big'
    MAXLENGTH = 200

    def __init__(self):
        pass

    @classmethod
    def decode(cls, content: bytes):
        #try:
        first_byte = int.from_bytes(content[0:1])
        # print(first_byte)
        #first_two_bits = (first_byte >> 6) & 0b11
        return TYPES[first_byte].decode(content)
        #except Exception as e:
        #    print("Failed to get type from packet", e)
        #    return


    def encode(self):
        raise NotImplementedError

    # for later perhaps
    def crc8_8_atm(msg): 
        crc = 0xFF
        for byte in msg:
            crc ^= byte
            for _ in range(8):
                crc = (crc << 1) ^ 0x07 if crc & 0x80 else crc << 1
            crc &= 0xff
        return crc ^ 0x00
    

class BroadcastPacket(DANPacket):
    """"""

    def __init__(self, source: int, id: int, content: str):
        super().__init__()
        self.type_bits = 0b00
        self.source = source
        self.id = id
        self.content = content

    def encode(self):
        self.raw_msg = self.type_bits.to_bytes(self.TYPEBITS, self.ENDIANNESS) + self.source.to_bytes(self.SOURCEBYTES, self.ENDIANNESS) + \
                       self.id.to_bytes(self.IDBYTES, self.ENDIANNESS) + self.content.encode(self.STRENCODING)
        return self.raw_msg
        
    @classmethod
    def decode(cls, content: bytes):
        source_start = cls.INFOBYTES
        source = int.from_bytes(content[source_start:source_start+cls.SOURCEBYTES])
        id_start = cls.INFOBYTES + cls.SOURCEBYTES
        id = int.from_bytes(content[id_start:id_start+cls.IDBYTES])
        content_start = cls.INFOBYTES + cls.SOURCEBYTES + cls.IDBYTES
        content = content[content_start:].decode(cls.STRENCODING)
        return BroadcastPacket(source, id, content)
    
    def same_header(self, rhs):
        if isinstance(rhs, BroadcastPacket):
            return self.source == rhs.source and self.id == rhs.id
        return False
    
    def __repr__(self):
        return f"source: {self.source} id: {self.id} content: {self.content}"
    
    def __eq__(self, value):
        if isinstance(value, BroadcastPacket):
            return self.source == value.source and self.id == value.id and self.content == value.content
        return False

class DMPacket(DANPacket):
    """"""

    def __init__(self, source: int, dest: int, id: int, content: str):
        super().__init__()
        self.type_bits = 0b01
        self.source = source
        self.id = id
        self.dest = dest
        self.content = content

    def encode(self):
        self.raw_msg = self.type_bits.to_bytes(self.TYPEBITS, self.ENDIANNESS) + self.source.to_bytes(self.SOURCEBYTES, self.ENDIANNESS) + \
                       self.dest.to_bytes(self.DESTBYTES, self.ENDIANNESS) + self.id.to_bytes(self.IDBYTES, self.ENDIANNESS) + \
                       self.content.encode(self.STRENCODING)
        return self.raw_msg
    
    @classmethod
    def decode(cls, content: bytes):
        source_start = cls.INFOBYTES
        source = int.from_bytes(content[source_start:source_start+cls.SOURCEBYTES])
        
        dest_start = source_start + cls.SOURCEBYTES
        dest = int.from_bytes(content[dest_start:dest_start+cls.DESTBYTES])

        id_start = dest_start + cls.DESTBYTES
        id = int.from_bytes(content[id_start:id_start+cls.IDBYTES])
        
        content_start = id_start + cls.IDBYTES
        content = content[content_start:].decode(cls.STRENCODING)
        return DMPacket(source, dest, id, content)
    

    def __repr__(self):
        return f"source: {self.source} dest: {self.dest} id: {self.id} content: {self.content}"
    
    def __eq__(self, value):
        if isinstance(value, DMPacket):
            return self.source == value.source and self.id == value.id and self.dest == value.dest and self.content == value.content
        return False



class MultiPartPacket(DANPacket):
    """"""

    def __init__(self, source: int, dest: int, id: int, seq: int, content: str):
        super().__init__()
        self.type_bits = 0b10
        self.source = source
        self.id = id
        self.seq = seq
        self.dest = dest
        self.content = content

    def encode(self):
        self.raw_msg = self.type_bits.to_bytes(self.TYPEBITS, self.ENDIANNESS) + self.source.to_bytes(self.SOURCEBYTES, self.ENDIANNESS) + \
                       self.dest.to_bytes(self.DESTBYTES, self.ENDIANNESS) + self.id.to_bytes(self.IDBYTES, self.ENDIANNESS) + \
                       self.seq.to_bytes(self.SEQBYTES, self.ENDIANNESS) + self.content.encode(self.STRENCODING)
        return self.raw_msg

    @classmethod
    def decode(cls, content: bytes):
        source_start = cls.INFOBYTES
        source = int.from_bytes(content[source_start:source_start+cls.SOURCEBYTES])
        
        dest_start = source_start + cls.SOURCEBYTES
        dest = int.from_bytes(content[dest_start:dest_start+cls.DESTBYTES])

        id_start = dest_start + cls.DESTBYTES
        id = int.from_bytes(content[id_start:id_start+cls.IDBYTES])
        
        seq_start = id_start + cls.IDBYTES
        seq = int.from_bytes(content[seq_start:seq_start+cls.SEQBYTES])
        
        content_start = seq_start + cls.SEQBYTES
        content = content[content_start:].decode(cls.STRENCODING)
        return MultiPartPacket(source, dest, id, seq, content)
    
    def __repr__(self):
        return f"source: {self.source} dest: {self.dest} id: {self.id} seq: {self.seq} content: {self.content}"
    
    def __eq__(self, value):
        if isinstance(value, MultiPartPacket):
            return self.source == value.source and self.id == value.id and self.dest == value.dest and self.seq == value.seq and self.content == value.content
        return False

class PingPacket(DANPacket):
    """"""

    def __init__(self, source: int, id: int):
        super().__init__()
        self.type_bits = 0b11
        self.source = source
        self.id = id

    def encode(self):
        self.raw_msg = self.type_bits.to_bytes(self.TYPEBITS, self.ENDIANNESS) + self.source.to_bytes(self.SOURCEBYTES, self.ENDIANNESS) + \
                       self.id.to_bytes(self.IDBYTES, self.ENDIANNESS)
        return self.raw_msg
    
    @classmethod
    def decode(cls, content: bytes):
        source_start = cls.INFOBYTES
        source = int.from_bytes(content[source_start:source_start+cls.SOURCEBYTES])
        
        id_start = cls.INFOBYTES + cls.SOURCEBYTES
        id = int.from_bytes(content[id_start:id_start+cls.IDBYTES])

        return PingPacket(source, id)
    
    def __repr__(self):
        return f"source: {self.source} id: {self.id}"
    
    def __eq__(self, value):
        if isinstance(value, PingPacket):
            return self.source == value.source and self.id == value.id
        return False
        

TYPES = {
    0b00: BroadcastPacket,
    0b01: DMPacket,
    0b10: MultiPartPacket,
    0b11: PingPacket
}


if __name__ == "__main__":
    print("Running tests")

    tests = [(1, 1, "Hello"), (0, 100, ""), (1000, 10, "!!!!")]

    for test in tests:
        a = BroadcastPacket(*test)
        b = DANPacket.decode(a.encode())
        assert(a == b)
    print("Broadcast Tests Passed")

    tests = [(1, 9, 1, "Hello"), (0, 1233, 100, ""), (1000, 0, 10, "!!!!")]

    for test in tests:
        a = DMPacket(*test)
        b = DANPacket.decode(a.encode())
        if (a != b): print(a.content == b.content, a.content, b.content, set(b.content) - set(a.content))
        assert(a == b)
    print("DM Tests Passed")

    tests = [(1, 9, 1, 0, "Hello"), (0, 1233, 100, 101, ""), (1000, 0, 10, 255, "!!!!")]

    for test in tests:
        a = MultiPartPacket(*test)
        b = DANPacket.decode(a.encode())
        if (a != b): print(a.content == b.content, a.content, b.content, set(b.content) - set(a.content))
        assert(a == b)
    print("MultiPacket Tests Passed")

    tests = [(1, 1), (0, 100), (1000, 10)]

    for test in tests:
        a = PingPacket(*test)
        b = DANPacket.decode(a.encode())
        assert(a == b)
    print("Ping Tests Passed")

