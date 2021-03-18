from coapthon.server.coap import CoAP
import Resource_PIR_Observe

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        self.add_resource('observe/', Resource_PIR_Observe.ObservableResource(coap_server=self))

def main():
    server = CoAPServer("192.168.137.8", 5683)
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")

if __name__ == '__main__':
    main()
