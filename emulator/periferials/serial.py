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
    p2p_connection = None
    income_byte_handler = None
    
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.keep_alive = True

    def start(self):
        threading.Thread(target=self._init_client, daemon=True).start()

    def stop(self):
        self.keep_alive = False

    def _init_client(self):
        try:
            self.socket.connect((HOST, PORT))
            self.p2p_connection = self.socket

            while self.keep_alive:
                byte = self.p2p_connection.recv(1)
                self.income_byte_handler(int.from_bytes(byte))

            self.p2p_connection.close()
        except:
            print(f"Error while processing client...")
            self.socket.close()

    def send_byte(self, value: int):
        try:
            if self.p2p_connection:
                self.p2p_connection.send(bytes([value]))
        except:
            print("Error while sending data to server...")
            self.p2p_connection = None
            self.income_byte_handler(0xFF)

    def register_incoming_handler(self, handler):
        self.income_byte_handler = handler

