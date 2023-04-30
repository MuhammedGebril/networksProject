import socket
import array
import sys
import http
import threading

"""
an interface that implements reliable data transfer using UDP
"""


class TCP:
    """
    Transport layer class that
    sends and recieves segments containing http messages reliably
    """

    TIMEOUT = 1

    def __init__(self, sockets, server_ip, server_port):
        self.server: socket.socket = sockets[0]
        self.client: socket.socket = sockets[1]
        self.server_add = (server_ip, server_port)
        self.client_add = None
        self.synchronise(server_ip, server_port)
        self.buffer = []
        self.cSeq = 0
        self.cAck = 0
        self.sSeq = 0
        self.sAck = 0

    def synchronise(self, server_ip, server_port):
        """
        responsible for synchronisation sequence

        :return: True if successful
        """

        self.client.sendto(Segment(1,0,0,0,0,"").serialize(),self.server_add)
        _, self.client_add = self.server.recvfrom(Segment.SEGMENTSIZE)
        self.server.sendto(Segment(1,1,0,0,1,"").serialize(),self.client_add)
        self.client.recv(Segment.SEGMENTSIZE)
        self.client.sendto(Segment(0,1,0,1,1,"").serialize(),self.server_add)
        self.server.recv(Segment.SEGMENTSIZE)
        self.cSeq = 1
        self.sSeq = 0
        self.cAck = 1
        self.sAck = 1

    def send(self, s2c: bool, msg: str):
        """
        sends http message from one host to the other

        :param s2c: specifies direction (server to client)
        :param msg: message to be sent
        :return: None
        """
        segments = Segment.getSegments(msg, self.sSeq if s2c else self.cSeq, self.sAck if s2c else self.cSeq)

        for segment in segments:
            if s2c:
                self.server.sendto(segment.serialize(), self.client_add)
            else:
                self.client.sendto(segment.serialize(), self.server_add)

            # lines to initiate receiving end
            rcv = threading.Thread(target=self.recieve, args=(self, s2c, self.sSeq if s2c else self.cSeq))
            rcv.start()

            # wait for ack otherwise resend
            if s2c:
                self.server.settimeout(TCP.TIMEOUT)
                ack = None
                while ack is None:
                    try:
                        ack = self.server.recv(4096)
                    except socket.timeout:
                        self.server.sendto(segment.serialize(), self.client_add)
                    valid, ack = Segment.parse(str(ack, "ascii"))

            else:
                self.client.settimeout(TCP.TIMEOUT)
                ack = None
                while ack is None:
                    try:
                        ack = self.client.recv(4096)
                    except socket.timeout:
                        self.client.sendto(segment.serialize(), self.server_add)
                    valid, ack = Segment.parse(str(ack, "ascii"))

    def recieve(self, s2c: bool, seq: int):
        """
        triggers reception at recieving end

        :param s2c: specifies direction (server to client)
        :param seq: sequence number
        :param akn: acknowledgment number
        :return: None
        """
        recieving = True
        # if the recipient is the client
        if s2c:
            while recieving:
                valid = False
                while not valid:
                    data = str(self.client.recv(4096), "ascii")
                    valid, data = Segment.parse(data)

                    if valid:
                        ack = Segment(0,1,0,seq,data.SEQ+1,"").serialize()
                        self.client.sendto(ack, self.server_add)
                self.buffer.append(data.Data)
                if data.DATA[len(data.Data)-1] == "\x04":
                    recieving = False
        else:
            while recieving:
                valid = False
                while not valid:
                    data = str(self.server.recv(4096), "ascii")
                    valid, data = Segment.parse(data)

                    if valid:
                        ack = Segment(0, 1, 0, seq, data.SEQ + 1, "").serialize()
                        self.client.sendto(ack, self.server_add)
                self.buffer.append(data.Data)
                if data.DATA[len(data.Data) - 1] == "\x04":
                    recieving = False

        msg = "".join(self.buffer)
        http.Http.parse(msg, s2c)


class Segment:
    """
    basic data unit sent by the transport layer
    contains all nessessary data to ensure reliable data transfer
    """
    SEGMENTSIZE = 4096

    def __init__(self, SYN: bool, ACK: bool, FIN: bool, SEQ: int, AKN: int, DATA: str):
        self.SYN = SYN
        self.ACK = ACK
        self.FIN = FIN
        self.SEQ = SEQ
        self.AKN = AKN
        self.DATA = DATA
        self.flags = [str(SYN), str(ACK), str(FIN), str(SEQ), str(AKN)]

    def get_flags_size(self):
        """
        returns size of segment flags
        :return: integer
        """
        size = 0
        for f in self.flags:
            size += sys.getsizeof(f)
        return size

    @staticmethod
    def getSegments(data: str, seq, ack):
        """
        divides message into several segments
        :param data: message to be sent
        :param seq: previous sequence number
        :param ack: previous acknowledgment number
        :return: segments to be sent
        """
        segments = []
        size = len(data)
        while size > 0:
            seg = Segment(0, 0, 0, seq, ack, "")
            fsize = seg.get_flags_size()
            if size < Segment.SEGMENTSIZE-2:
                seg.DATA = "".join(data[:size], "\x04")
            else:
                seg.DATA = data[:Segment.SEGMENTSIZE - fsize - 2]
                data = data[Segment.SEGMENTSIZE-fsize-2:]
            size -= Segment.SEGMENTSIZE-fsize-2
            seq += Segment.SEGMENTSIZE-fsize-2
            ack += 1
            segments.append(seg)

        return segments


    @staticmethod
    def computeChecksum(self = None, arg = None):
        """
        computes checksum of segment
        :return: integer
        """
        chk = 0
        segment = "_"
        if arg is None:
            segment = segment.join([self.flags, self.DATA])
        else:
            segment = segment.join(str(arg, 'ascii'))
        packet = bytes(segment, 'ascii')
        if len(packet) % 2 != 0:
            packet += b'\0'
        res = sum(array.array("H", packet))
        res = (res >> 16) + (res & 0xffff)
        res += res >> 16
        chk = (~res) & 0xffff
        return chk

    def serialize(self):
        """
        converts segment into Byte-array form
        :return: byte-array
        """
        checksum = Segment.computeChecksum(self)
        flags = self.flags.append([str(checksum), self.DATA])

        segment = "_"
        segment = segment.join(flags)
        byte = bytes(segment, 'utf-8')
        return byte

    @staticmethod
    def parse(msg: str):
        """
        converts Byte-array into segment form
        :return: Segment object
        """
        msg = msg.split('_', 6)
        checksum = msg.pop(5)
        computedCheckSum = Segment.computeChecksum(arg=msg)
        if checksum == computedCheckSum:
            return Segment(msg[0], msg[1], msg[2], msg[3], msg[4], msg[6])
        else:
            return None
