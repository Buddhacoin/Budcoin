import socket
import threading
import json
import time
import hashlib
import secrets

# Класс для транзакций
class Transaction:
    def __init__(self, sender, receiver, amount, timestamp):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        tx_string = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hashlib.sha256(tx_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "hash": self.hash
        }

# Класс для блоков
class Block:
    def __init__(self, timestamp, transactions, previous_hash, nonce=0, miner_address=None):
        self.timestamp = timestamp
        self.transactions = transactions  # Список транзакций
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.miner_address = miner_address
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        tx_hashes = "".join(tx.hash for tx in self.transactions)
        block_string = f"{self.timestamp}{tx_hashes}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

# Класс для узла Budcoin
class BudcoinNode:
    def __init__(self, host='127.0.0.1', port=5000, miner_address=None):
        self.host = host
        self.port = port
        self.peers = []
        self.miner_address = miner_address or secrets.token_hex(32)  # Уникальный адрес майнера
        self.chain = []
        self.pending_transactions = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.target_difficulty = "000000"  # Сложность PoW: хэш начинается с 5 нулей
        self.halving_interval = 210000  # Халвинг каждые 210,000 блоков
        self.initial_reward = 50  # Начальная награда 50 BDC
        self.load_chain()
        print(f"Узел запущен на {self.host}:{self.port}")
        print(f"Адрес майнера: {self.miner_address}")
        print(f"Длина цепочки: {len(self.chain)} блоков")
        print(f"Баланс: {self.get_balance(self.miner_address)} BDC")

    def load_chain(self):
        try:
            with open(f"chain_{self.port}.json", "r") as f:
                chain_data = json.load(f)
                self.chain = []
                for block_data in chain_data:
                    transactions = [Transaction(**tx) for tx in block_data["transactions"]]
                    block = Block(block_data["timestamp"], transactions, block_data["previous_hash"], block_data["nonce"], block_data["miner_address"])
                    self.chain.append(block)
        except:
            genesis_block = Block(time.time(), [], "0", 0, "genesis_miner")
            self.chain.append(genesis_block)
            self.save_chain()

    def save_chain(self):
        with open(f"chain_{self.port}.json", "w") as f:
            chain_data = []
            for block in self.chain:
                block_data = {
                    "timestamp": block.timestamp,
                    "transactions": [tx.to_dict() for tx in block.transactions],
                    "previous_hash": block.previous_hash,
                    "nonce": block.nonce,
                    "miner_address": block.miner_address,
                    "hash": block.hash
                }
                chain_data.append(block_data)
            json.dump(chain_data, f)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
            if block.miner_address == address:
                block_height = len(self.chain) - 1
                reward = self.initial_reward // (2 ** (block_height // self.halving_interval))
                balance += max(reward, 1)  # Минимальная награда 1 BDC
        return balance

    def create_transaction(self, sender, receiver, amount):
        if sender != "reward" and self.get_balance(sender) < amount:
            print(f"Недостаточно средств у {sender} для отправки {amount} BDC")
            return False
        tx = Transaction(sender, receiver, amount, time.time())
        self.pending_transactions.append(tx)
        self.broadcast(f"NEW_TX:{json.dumps(tx.to_dict())}")
        print(f"Создана транзакция: {sender} -> {receiver} {amount} BDC")
        return True

    def connect_to_peer(self, peer_host, peer_port):
        try:
            peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_sock.connect((peer_host, peer_port))
            self.peers.append(peer_sock)
            print(f"Подключился к узлу {peer_host}:{peer_port}")
            peer_sock.send("REQUEST_CHAIN".encode())
        except Exception as e:
            print(f"Не удалось подключиться к {peer_host}:{peer_port}: {e}")

    def handle_client(self, conn, addr):
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                if data == "REQUEST_CHAIN":
                    chain_data = json.dumps([{"timestamp": block.timestamp, "transactions": [tx.to_dict() for tx in block.transactions], "previous_hash": block.previous_hash, "nonce": block.nonce, "miner_address": block.miner_address, "hash": block.hash} for block in self.chain])
                    conn.send(f"CHAIN:{chain_data}".encode())
                elif data.startswith("CHAIN:"):
                    chain_data = json.loads(data[len("CHAIN:"):])
                    new_chain = []
                    for block_data in chain_data:
                        transactions = [Transaction(**tx) for tx in block_data["transactions"]]
                        block = Block(block_data["timestamp"], transactions, block_data["previous_hash"], block_data["nonce"], block_data["miner_address"])
                        new_chain.append(block)
                    if len(new_chain) > len(self.chain) and self.is_valid_chain(new_chain):
                        self.chain = new_chain
                        self.save_chain()
                        print(f"Цепочка обновлена, длина: {len(self.chain)}")
                elif data.startswith("NEW_BLOCK:"):
                    block_data = json.loads(data[len("NEW_BLOCK:"):])
                    transactions = [Transaction(**tx) for tx in block_data["transactions"]]
                    new_block = Block(block_data["timestamp"], transactions, block_data["previous_hash"], block_data["nonce"], block_data["miner_address"])
                    if self.is_valid_block(new_block, self.chain[-1]):
                        self.chain.append(new_block)
                        self.save_chain()
                        print(f"Добавлен новый блок от {addr}, длина цепочки: {len(self.chain)}")
                        print(f"Баланс: {self.get_balance(self.miner_address)} BDC")
                elif data.startswith("NEW_TX:"):
                    tx_data = json.loads(data[len("NEW_TX:"):])
                    tx = Transaction(**tx_data)
                    if tx not in self.pending_transactions:
                        self.pending_transactions.append(tx)
                        print(f"Получена транзакция: {tx.sender} -> {tx.receiver} {tx.amount} BDC")
            except:
                break
        conn.close()

    def is_valid_chain(self, chain):
        for i in range(1, len(chain)):
            if chain[i].hash != chain[i].calculate_hash():
                return False
            if chain[i].previous_hash != chain[i-1].hash:
                return False
            if not self.is_valid_proof(chain[i]):
                return False
            for tx in chain[i].transactions:
                if tx.hash != tx.calculate_hash():
                    return False
                if tx.sender != "reward" and self.calculate_balance(chain[:i], tx.sender) < tx.amount:
                    return False
        return True

    def calculate_balance(self, chain, address):
        balance = 0
        for block in chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
            if block.miner_address == address:
                block_height = len(chain) - 1
                reward = self.initial_reward // (2 ** (block_height // self.halving_interval))
                balance += max(reward, 1)
        return balance

    def is_valid_block(self, block, previous_block):
        if block.previous_hash != previous_block.hash:
            return False
        if block.hash != block.calculate_hash():
            return False
        if not self.is_valid_proof(block):
            return False
        return True

    def is_valid_proof(self, block):
        return block.hash.startswith(self.target_difficulty)

    def proof_of_work(self, block):
        block.nonce = 0
        while not block.hash.startswith(self.target_difficulty):
            block.nonce += 1
            block.hash = block.calculate_hash()
        return block

    def mine_block(self):
        previous_block = self.chain[-1]
        block_height = len(self.chain)
        reward = self.initial_reward // (2 ** (block_height // self.halving_interval))
        reward = max(reward, 1)  # Минимальная награда 1 BDC
        reward_tx = Transaction("reward", self.miner_address, reward, time.time())
        transactions = [reward_tx] + self.pending_transactions[:10]  # Берем до 10 транзакций
        new_block = Block(time.time(), transactions, previous_block.hash, 0, self.miner_address)
        new_block = self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.pending_transactions = self.pending_transactions[len(transactions)-1:]  # Удаляем обработанные транзакции
        self.save_chain()
        print(f"Намайнил блок: {new_block.hash}, Награда: {reward} BDC, Транзакций: {len(transactions)}")
        print(f"Баланс: {self.get_balance(self.miner_address)} BDC")
        block_data = {"timestamp": new_block.timestamp, "transactions": [tx.to_dict() for tx in new_block.transactions], "previous_hash": new_block.previous_hash, "nonce": new_block.nonce, "miner_address": new_block.miner_address, "hash": new_block.hash}
        self.broadcast(f"NEW_BLOCK:{json.dumps(block_data)}")

    def mine_block_loop(self):
        while True:
            self.mine_block()
            time.sleep(10)

    def broadcast(self, message):
        for peer in self.peers:
            try:
                peer.send(message.encode())
            except:
                self.peers.remove(peer)

    def start(self):
        mining_thread = threading.Thread(target=self.mine_block_loop)
        mining_thread.daemon = True
        mining_thread.start()
        try:
            while True:
                conn, addr = self.sock.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("Остановка узла...")
            self.sock.close()
            exit(0)

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    peer_host = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
    peer_port = int(sys.argv[3]) if len(sys.argv) > 3 else 5001
    node = BudcoinNode(port=port)
    if peer_host and peer_port:
        node.connect_to_peer(peer_host, peer_port)
    node.start()