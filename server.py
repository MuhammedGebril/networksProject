import http

localIP = "127.0.0.1"
localPort = 20001

# Create a http interface
http = http.Http(localIP, localPort)
print("UDP server up and listening")
# Listen for incoming datagrams


def handle(method, url, length=None, data=""):
    """
    handles http requests
    """
    if method == "GET":
        http.send(True, code=200, status="ok", payload="\n".join(open(url, "r").readlines()))
    else:
        file = open(url, "a")
        file.write(data)
        http.send(True, code=200, status="ok")
