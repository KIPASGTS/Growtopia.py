import struct
import enet

class Variants:
    def __init__(self, delay = 0, NetID = -1):
        self.index = 0
        self.len = 61
        self.packetData = bytearray(61)

        struct.pack_into('<I', self.packetData, 0, 4)           # message type
        struct.pack_into('<I', self.packetData, 4, 1)           # packet type variant
        struct.pack_into('<i', self.packetData, 8, NetID)       # netid
        struct.pack_into('<I', self.packetData, 16, 8)          # characterState
        struct.pack_into('<I', self.packetData, 24, delay)      # delay

    def InsertInt(self, a1):
        data = bytearray(self.len + 2 + 4)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x9
        struct.pack_into('<I', data, self.len + 2, a1)
        self.index += 1
        self.packetData = data
        self.len += 2 + 4
        self.packetData[60] = self.index

    def Insertint(self, a1):
        data = bytearray(self.len + 2 + 4)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x9
        struct.pack_into('<I', data, self.len + 2, a1)
        self.index += 1
        self.packetData = data
        self.len += 2 + 4
        self.packetData[60] = self.index

    def InsertUint(self, a1):
        data = bytearray(self.len + 2 + 4)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x5
        struct.pack_into('<I', data, self.len + 2, a1)
        self.index += 1
        self.packetData = data
        self.len += 2 + 4
        self.packetData[60] = self.index

    def InsertFloat(self, a1):
        data = bytearray(self.len + 2 + 4)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x1
        struct.pack_into('<I', data, self.len + 2, struct.unpack('<I', struct.pack('<f', a1))[0])
        self.index += 1
        self.packetData = data
        self.len += 2 + 4
        self.packetData[60] = self.index
    
    def Insertfloat(self, a1):
        data = bytearray(self.len + 2 + 4)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x1
        struct.pack_into('<I', data, self.len + 2, struct.unpack('<I', struct.pack('<f', a1))[0])
        self.index += 1
        self.packetData = data
        self.len += 2 + 4
        self.packetData[60] = self.index
        
    def InsertVector2F(self, a1, a2):
        data = bytearray(self.len + 2 + 8)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x3
        struct.pack_into('<I', data, self.len + 2, struct.unpack('<I', struct.pack('<f', a1))[0])
        struct.pack_into('<I', data, self.len + 6, struct.unpack('<I', struct.pack('<f', a2))[0])
        self.index += 1
        self.packetData = data
        self.len += 2 + 8
        self.packetData[60] = self.index

    def InsertVector3F(self, a1, a2, a3):
        data = bytearray(self.len + 2 + 12)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x4
        struct.pack_into('<I', data, self.len + 2, struct.unpack('<I', struct.pack('<f', a1))[0])
        struct.pack_into('<I', data, self.len + 6, struct.unpack('<I', struct.pack('<f', a2))[0])
        struct.pack_into('<I', data, self.len + 10, struct.unpack('<I', struct.pack('<f', a3))[0])
        self.index += 1
        self.packetData = data
        self.len += 2 + 12
        self.packetData[60] = self.index

    def InsertString(self, a1: str):
        data = bytearray(self.len + 2 + len(a1) + 4)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x2
        struct.pack_into('<I', data, self.len + 2, len(a1))
        data[self.len + 6:self.len + 6 + len(a1)] = a1.encode('utf-8')
        self.index += 1
        self.packetData = data
        self.len += 2 + len(a1) + 4
        self.packetData[60] = self.index

    def Insertstr(self, a1: str):
        data = bytearray(self.len + 2 + len(a1) + 4)
        data[:self.len] = self.packetData
        data[self.len] = self.index
        data[self.len + 1] = 0x2
        struct.pack_into('<I', data, self.len + 2, len(a1))
        data[self.len + 6:self.len + 6 + len(a1)] = a1.encode('utf-8')
        self.index += 1
        self.packetData = data
        self.len += 2 + len(a1) + 4
        self.packetData[60] = self.index

    def Send(self, peer):
        enetPacket = enet.Packet(data=self.packetData, flags=enet.PACKET_FLAG_RELIABLE)
        peer.send(0, enetPacket)

    def CreateFromArgv(self, *args):
        for arg in args:
            if isinstance(arg, (int, str, float)):
                getattr(self, f'Insert{type(arg).__name__}')(arg)
            elif isinstance(arg, list) and all(isinstance(item, float) for item in arg):
                getattr(self, f'InsertVector{len(arg)}F')(*arg)


            

