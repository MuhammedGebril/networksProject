import http

localIP = "127.0.0.1"
localPort = 20001

# Create a http interface
http = http.Http(localIP, localPort)
print("UDP server up and listening")
# Listen for incoming datagrams


def handle(method,url,length=None,data=""):
    """
    handles http requests
    """
    pass


# UDPServerSocket.sendto(bytesToSend, address)
