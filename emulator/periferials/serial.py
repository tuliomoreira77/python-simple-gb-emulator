import socket
import threading


HOST = 'localhost'
PORT = 43251

class MockNetAdapter:

    def start(self):
        pass

    def stop(self):
        pass

    def send_byte(self, value: int):
        pass

    def register_incoming_handler(self, handler):
        pass


class SimpleNetworkAdapter:
    in_use = False
    p2p_connection = None
    income_byte_handler = None
        
    def start(self):
        self.in_use = True
        self.keep_alive = True
        self.p2p_connection = None
        threading.Thread(target=self._init_client, daemon=True).start()

    def stop(self):
        print("Disconnection from server")
        try:
            self.p2p_connection.shutdown(socket.SHUT_RDWR)
            self.p2p_connection.close()
        except:
            pass

        self.keep_alive = False
        self.p2p_connection = None
        self.in_use = False

    def _init_client(self):
        try:
            print("Connecting to serial server...")
            self.p2p_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.p2p_connection.connect((HOST, PORT))
            print("Connected!")

            while self.keep_alive:
                byte = self.p2p_connection.recv(1)
                self.income_byte_handler(int.from_bytes(byte))
                
        except:
            print(f"Error while processing client...")
            self.stop()

    def send_byte(self, value: int):
        try:
            if self.p2p_connection:
                self.p2p_connection.send(bytes([value]))
        except:
            print("Error while sending data to server...")
            self.stop()
            self.income_byte_handler(0xFF)

    def register_incoming_handler(self, handler):
        self.income_byte_handler = handler

