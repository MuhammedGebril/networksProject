import client
import server
import socket
import tcp

"""
an interface for sending and recieving http messages
"""


class Http:
    """
    Application layer class
    this file will be http class , the object to be sent to the transport layer to be sent using reliable modified UDP
    """

    def __init__(self, host=None, port=None):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        if self.sockets is None:
            sock.bind((host,port))
        self.sockets.append(sock)
        if len(self.sockets) == 2:
            self.connection = tcp.TCP(self.sockets, host, port)

    def send(self, is_response: bool, method="GET", url=None, code=None, status=None, payload: str=None):
        """
        responsible for sending http requests and responses
        """

        http = ""
        if is_response:
            "".join([http, "HTTP/1.1 {code:d} {status}\n".format(code = code,status = status)])
            additional_response_headers = "Content-Length: {size}\nContent-Type: text/html; charset=utf-8\n\n".format(len(payload))
            "".join([http, additional_response_headers])
            "".join([http, payload])

        else:
            "".join([http, "{method} {url} HTTP/1.1\n".format(method = method.upper(), url = url)])
            if method.upper() == "POST":
                additional_request_headers = "Content-Length: {size}\n\n".format(len(payload))
                "".join([http, additional_request_headers])
                "".join([http, payload])

        self.connection.send(is_response, http)


    @staticmethod
    def parse(msg: str, is_response: bool):
        """
        responsible for parsing recieved http requests and responses
        :param msg: message to be parsed
        :param is_response: indicates if that message is from the server or not
        :return: None
        """

        msg = msg.partition('\n\n')
        headers = msg[0]
        data = msg[2]
        headers = headers.split('\n')

        if is_response:
            code = headers[0].split(' ')[1]
            status = headers[0].split(' ')[2]
            length = headers[1].split(' ')[1]
            client.recieve(code, status, length, data)

        else:
            method = headers[0].split(' ')[0]
            url = headers[0].split(' ')[1]
            length = None
            if method == "POST":
                length = headers[1].split(' ')[1]
            server.handle(method, url, length, data)





