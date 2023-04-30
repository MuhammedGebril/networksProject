import socket
import http

# Create a http interface
http = http.Http("localhost", 20001)
http.send(False, url="/book.txt")


def recieve(code, status, length=None, data=None):
    """
    recieves server response
    """
    if data:
        print(data)
    else:
        print(code, status)

