import socket
import threading
import json
import time

class BudcoinNode:
    def __init__(self, host='127.0.0.1', port=5001):
        self.host = host
        self.port = port
        self.peers = []
        self.wallet = self.load_balance()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print(f"Узел запущен на {self.host}:{self.port}")
        print(f"Баланс: {self.wallet} BDC")

    def load_balance(self):
        try:
            with open(f"balance_{self.port}.json", "r") as f:
                data = json.load(f)
                return data["balance"]
        except:
            return 0

    def save_balance(self):
        with open(f"balance_{self.port}.json", "w") as f:
            json.dump({"balance": self.wallet}, f)

    def connect_to_peer(self, peer_host, peer_port):
        try:
            peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_sock.connect((peer_host, peer_port))
            self.peers.append(peer_sock)
            print(f"Подключился к узлу {peer_host}:{peer_port}")
        except Exception as e:
            print(f"Не удалось подключиться к {peer_host}:{peer_port}: {e}")

    def handle_client(self, conn, addr):
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(f"Получено от {addr}: {data}")
                self.broadcast(data)
            except:
                break
        conn.close()

    def broadcast(self, message):
        for peer in self.peers:
            try:
                peer.send(message.encode())
            except:
                self.peers.remove(peer)

    def mine_block(self):
        block = f"Block mined at {time.time()}"
        self.wallet += 50  # Награда 50 BDC
        print(f"Намайнил блок: {block}, Баланс: {self.wallet} BDC")
        self.save_balance()
        self.broadcast(f"New block: {block}")

    def mine_block_loop(self):
        while True:
            self.mine_block()
            time.sleep(10)

    def start(self):
        mining_thread = threading.Thread(target=self.mine_block_loop)
        mining_thread.start()
        while True:
            conn, addr = self.sock.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    node = BudcoinNode(port=5001)
    node.connect_to_peer('127.0.0.1', 5000)
    node.start()