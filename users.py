from horu import Http

# server function
def handle(method, url, length=None, data=""):
    """
    handles http requests
    """
    if method == "GET":
        try:
            data = open(url[1:], "r").readlines()
            code = 200
            status = "OK"
        except FileNotFoundError:
            data = ""
            code = 404
            status = "Not Found"
        http.send(True, code=code, status=status, payload="".join(data))
    else:
        try:
            file = open(url[1:], "a")
            file.write(data)
            code = 200
            status = "OK"
        except FileNotFoundError:
            code = 404
            status = "Not Found"
        http.send(True, code=code, status=status)


# client function
def recieve(code, status, length=None, data=None):
    """
    recieves server response
    """
    print(code, status)
    if data:
        print(data)



localIP = "127.0.0.1"
localPort = 20001

# Create a http interface
http = Http(handle, localIP, localPort)
print("HTTP server up and listening")
# Listen for incoming datagrams

Http(recieve, "localhost", 20001)
http.send(False, url="/book.txt")
