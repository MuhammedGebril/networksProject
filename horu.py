import socket
import tcp
"""
HTTP Over Reliable UDP
an interface for sending and recieving http messages
"""


class Http:
    """
    Application layer class
    this file will be http class , the object to be sent to the transport layer to be sent using reliable modified UDP
    """
    current_connection = None

    def __init__(self, callback, host, port):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        if not Http.current_connection:
            self.sockets = []
            Http.current_connection = self
        if len(Http.current_connection.sockets) == 0:
            sock.bind((host, port))
            Http.current_connection.handle = callback
        Http.current_connection.sockets.append(sock)
        if len(Http.current_connection.sockets) == 2:
            Http.current_connection.recieve = callback
            Http.current_connection.tcp_connection = tcp.TCP(Http.current_connection.sockets, host, port)

    def send(self, is_response: bool, method="GET", url=None, code=None, status=None, payload: str=None):
        """
        responsible for sending http requests and responses
        """

        http = ""
        if is_response:
            http = "".join([http, "HTTP/1.1 {code:d} {status}\n".format(code = code,status = status)])
            additional_response_headers = "Content-Length: {}\nContent-Type: text/html; charset=utf-8\n\n".format(len(payload))
            http = "".join([http, additional_response_headers])
            http = "".join([http, payload])
        else:
            http = "".join([http, "{method} {url} HTTP/1.1\n".format(method = method.upper(), url = url)])
            if method.upper() == "POST":
                additional_request_headers = "Content-Length: {}\n\n".format(len(payload))
                http = "".join([http, additional_request_headers])
                http = "".join([http, payload])

        Http.current_connection.tcp_connection.send(is_response, http)


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
            print(headers)
            code = headers[0].split(' ')[1]
            status = " ".join(headers[0].split(' ')[2:])
            length = headers[1].split(' ')[1]
            Http.current_connection.recieve(code, status, length, data)

        else:
            method = headers[0].split(' ')[0]
            url = headers[0].split(' ')[1]
            length = None
            if method == "POST":
                length = headers[1].split(' ')[1]
            Http.current_connection.handle(method, url, length, data)





