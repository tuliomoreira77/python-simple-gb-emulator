import socket
import threading

HOST = 'localhost'
PORT = 43251

class BasicSerialServer:

    socket = None
    gameboy_1 = None
    gameboy_2 = None
    keep_alive = True

    def create_link(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(2)
        print("Waiting gameboys connect...")
        client_socket, client_address = self.socket.accept()
        print(f"Gameboy1 Conected {client_address}")
        self.gameboy_1 = client_socket
        client_socket, client_address = self.socket.accept()
        self.gameboy_2 = client_socket
        print(f"Gameboy2 Conected {client_address}")
        print(f"Serial link stablished")

        g1_thread = threading.Thread(target=self.handle_gameboy_1, daemon=True)
        g2_thread = threading.Thread(target=self.handle_gameboy_2, daemon=True)

        return g1_thread, g2_thread
        

    def handle_gameboy_1(self):
        try:
            while self.keep_alive:
                self.gameboy_2.send(self.gameboy_1.recv(1))
        except:
            self._clean()

    def handle_gameboy_2(self):
        try:
            while self.keep_alive:
                self.gameboy_1.send(self.gameboy_2.recv(1))
        except:
            self._clean()

    def _clean(self):
        print("Link disconnected... Cleanning")
        self.keep_alive = False

        try:
            self.gameboy_1.shutdown(socket.SHUT_RDWR)
            self.gameboy_1.close()
        except:
            pass
        
        try:
            self.gameboy_2.shutdown(socket.SHUT_RDWR)
            self.gameboy_2.close()
        except:
            pass

        try:
            self.socket.close()
        except:
            pass

        print("Cleanned...")

    def _flush(self, source):
        source.setblocking(False)
        try:
            while True:
                data = source.recv(128)
                if not data:
                    break
        except:
            pass
        source.setblocking(True)



if __name__ == "__main__":
    print("Starting basic serial server...")
    while True:
        try:
            server = BasicSerialServer()
            t1, t2 = server.create_link()
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            print("")
            print("")
        except:
            print("Error creating link")
            break

    

        
