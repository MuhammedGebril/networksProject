import socket
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
        self.synchronise(server_ip, server_port)

    def synchronise(self, server_ip, server_port):
        """
        responsible for synchronisation sequence

        :return: True if successful
        """
        pass

    def send(self, s2c: bool, msg: str):
        """
        sends http message from one host to the other

        :param s2c: specifies direction (server to client)
        :param msg: message to be sent
        :return: None
        """

        dummy = None
        # lines to initiate receiving end
        rcv = threading.Thread(target=self.recieve, args=(self, s2c, dummy, dummy))
        rcv.start()

        # wait for ack otherwise resend
        if s2c:
            self.server.settimeout(TCP.TIMEOUT)
            ack = None
            while ack is None:
                try:
                    ack = self.server.recv(4096)
                except socket.timeout:
                    pass  # code to handle timeout

        else:
            self.client.settimeout(TCP.TIMEOUT)
            ack = None
            while ack is None:
                try:
                    ack = self.client.recv(4096)
                except socket.timeout:
                    pass  # code to handle timeout

    def recieve(self, s2c: bool, seq: int, akn: int):
        """
        triggers reception at recieving end

        :param s2c: specifies direction (server to client)
        :param seq: sequence number
        :param akn: acknowledgment number
        :return: None
        """
        # if the recipient is the client
        if s2c:
            try:
                data = str(self.client.recv(4096), "utf-8")
            except socket.timeout:
                pass  # code to handle timeout

            ack = Segment(0,1,0,seq,akn,"").serialize()
            self.client.sendto(ack, self.server_add)


class Segment:
    """
    basic data unit sent by the transport layer
    contains all nessessary data to ensure reliable data transfer
    """

    def __init__(self, SYN: bool, ACK: bool, FIN: bool, SEQ: int, AKN: int, DATA: str):
        self.SYN = SYN
        self.ACK = ACK
        self.FIN = FIN
        self.SEQ = SEQ
        self.AKN = AKN
        self.DATA = DATA

    def computeChecksum(self):
        """
        computes checksum of segment
        :return: integer
        """
        chk = 0

        return chk

    def serialize(self):
        """
        converts segment into Byte-array form
        :return: byte-array
        """
        bytes = ""
        checksum = self.computeChecksum()
        return bytes


    def parse(self):
        """
        converts Byte-array into segment form
        :return: Segment object
        """

        #return Segment(s,a,f,sq,ak,dt)