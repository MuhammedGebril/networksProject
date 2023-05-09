from horu import Http

client_requests = [(False, "Post", "/contacts.txt", None, None, "John Smith --- 0123456789\n"), (False, "Get", "/contacts.txt")]
client_counter = 0


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
            open(url[1:]).close()
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
    print()
    global client_counter
    if client_counter < len(client_requests):
        client_counter = client_counter + 1
        http.send(*(client_requests[client_counter-1]))


localIP = "127.0.0.1"
localPort = 20001
# Create a http interface
http = Http(handle, localIP, localPort)
print("HTTP server up and listening\n")
# Listen for incoming datagrams

Http(recieve, "localhost", 20001)
http.send(False, method="POST", url="/book.txt", payload="\nPOST TEST\n")
