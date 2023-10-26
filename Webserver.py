import socket
import sys

class WebServer:
    #specify host and port for server
    def __init__(instance, host = "127.0.0.1", port = 8888):
        instance.map = table()
        instance.host = host
        instance.port = port

    #socket is created and bound to host and port specified in initialize
    def start(self):
    # Create a server socket and bind it to the specified host and port
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((self.host, self.port))

        try:
        # Server enters listening state
            server_sock.listen()
            print("The server is listening at {}:{}".format(self.host, self.port))

            while True:
            # Accept incoming client connections
                client_sock, client_address = server_sock.accept()

                try:
                    while True:
                    # Create a request object for processing
                        request = Request(self.map, client_sock)
                        response = request.process()

                    # If there is no response, exit the loop
                        if not response:
                            break

                    # Send the response back to the client
                        client_sock.send(response.to_bytes())
                finally:
                # Close the client socket
                    client_sock.close()
        finally:
        # Close the server socket
            server_sock.close()


#handles processing of incomming requests
class Request:
    def __init__(instance, map, socket):
        instance.map = map
        instance.socket = socket

    def process(instance):
        header = instance.read_header()
        if not header:
            return None

        if "/key/" == header["path"][:5]:
            return instance.keyvals_requests(header)
        elif "/counter/" == header["path"][:9]:
            return instance.counter_requests(header)

    def keyvals_requests(instance, header):

        key = header["path"][5:]
        if header["method"] == "post":
            #print("a post")
            content_length = int(header["other"]["content-length"])
            body = instance.read_body(content_length)
            data = instance.map.get_keyval(key)
            data2 = instance.map.get_counter(key)
            if data == None:
                instance.map.update_keyval(key, body)
                return Response(200)
            elif data2 != None and data2 > 0:
                return Response(405)
            else:
                instance.map.update_keyval(key, body)
                return Response(200)

        elif header["method"] == "get":
            data = instance.map.get_keyval(key)
            data2 = instance.map.get_counter(key)
            if data == None and data2 == None:
                return Response(404)

            elif data2 == None:
                #print(data)
                return Response(200, data)
            elif data2 != None and data2 > 0:
                instance.map.decrement_counter( key)
                data3 = instance.map.get_counter(key)

                if data3 == 0:
                    instance.map.del_keyval(key)
                    instance.map.del_counter(key)
                #print(data)
                return Response(200, data)

            return Response(200, data)

        elif header["method"] == "delete":
            #print("a delete")
            data = instance.map.get_keyval(key)
            if data == None:
                return Response(404)
            #print(".")
            data2 = instance.map.get_counter(key)
            #print("/")
            if data2 == None:
                #print("deleted")
                data3 = instance.map.del_keyval(key)
                return Response(200, data3)
            if data2 > 0:
                #print("can't delete")
                return Response(405)
            else:
                #print("deleted")
                data3 = instance.map.del_keyval(key)
                return Response(200, data)

    def counter_requests(instance, header):
        #print("Hi")
        key = header["path"][9:]
        #content_length = int(header["other"]["content-length"])
        #body = instance.read_body(content_length)
        if header["method"] == "post":
            content_length = int(header["other"]["content-length"])
            body = instance.read_body(content_length)
            #print("a post")
            data = instance.map.get_keyval(key)
            if data == None:
                #print("Counter POST: Data not found")
                return Response(405)
            instance.map.update_counter(key, int(body))
            #print("Counter POST: Counter updated")
            return Response(200)
        if header["method"] == "get":
            #print("a get counter")
            data1 = instance.map.get_keyval(key)
            if data1 == None:
                #print("Counter GET: Data not found")
                return Response(404)
            data = instance.map.get_counter(key)
            if data == None:
                #print("Counter GET: Counter not found")
                return Response(200, "Infinity".encode())
                #return  "200 OK Content-Length 8 Infinity".encode()
                #response = "200 OK Content-Length 8  Infinity"
                #return response.encode()
            else:
                #print("Counter GET: Counter value:", (data))
                return Response(200, str(data).encode())
        elif header["method"] == "delete":
            data = instance.map.get_counter(key)
            if data == None:
                #print("Counter DELETE: Counter not found")
                return Response(404)
            instance.map.del_counter(key)
            #instance.map.del_keyval(key)
            #print("Counter DELETE: Key deleted")
            return Response(200, str(data).encode())



    def read_header(instance):
        # Reading Header
        header = []
        substring = []
        while True:
            data = instance.socket.recv(1)
            if not data:
                break
            data = data.decode()
            if data != " ":
                substring.append(data)
            elif data == " " and substring:
                header.append("".join(substring))
                substring = []
            else:
                break

        # Parsing Header
        parsed_header = {}
        if header:
            parsed_header["method"] = header[0].lower()
            parsed_header["path"] = header[1]
            parsed_header["other"] = {}
            for i in range(2, len(header) - 1, 2):
                parsed_header["other"][header[i].lower()] = header[i + 1]
        return parsed_header

    def read_body(instance, content_length):
        content = bytes()
        while content_length > 0:
            data = instance.socket.recv(content_length)
            if not data:
                break
            content += data
            content_length -= len(data)
        return content

#construct http like responses
class Response:
    CODES = {
        200: "OK",
        404: "NotFound",
        405: "MethodNotAllowed"

    }

    def __init__(instance, status_code, data = None):
        instance.status_code = status_code
        instance.status_msg = instance.CODES[status_code]
        instance.headers = {}
        instance.data = data
        if data == "Infinity":
            instance.headers["content-length"] = len("Infinity")
            data = data.encode()
        if data != None:
            instance.headers["content-length"] = len(instance.data)
        #else:
         #   instance.headers["content-length"] = 0

    def to_bytes(instance):
        output = "{} {}".format(instance.status_code, instance.status_msg)
        for key, val in instance.headers.items():
            output += " {} {}".format(key, val)
        output = (output + "  ").encode()

        if instance.data != None:

            output = output + instance.data
        return output


class table:
    def __init__(instance):
        instance.keyvals = {}
        instance.counters = {}

    def update_keyval(instance, key, value):
        instance.keyvals[key] = value

    def get_keyval(instance, key):
        return instance.keyvals.get(key)

    def del_keyval(instance, key):
        return instance.keyvals.pop(key, None)
    def del_counter(instance, key):
        return instance.counters.pop(key, None)


    def update_counter(instance, key, value):
        if key not in instance.counters:
            instance.counters[key] = 0
        instance.counters[key] += value

    def decrement_counter(instance, key):
        if key not in instance.counters:
            instance.counters[key] = 0
        instance.counters[key] -= 1

    def get_counter(instance, key):
        return instance.counters.get(key)

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python3 WebServer-A0266319X.py <port>")
        exit(1)
    WebServer(port = int(sys.argv[1])).start()# blank
