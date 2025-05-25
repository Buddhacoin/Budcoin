import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data  # Транзакции или сообщения
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{json.dumps(self.data)}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Budcoin:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4  # Сложность майнинга (4 ведущих нуля в хэше)
        self.max_supply = 21000000  # 21 миллион BDC
        self.current_supply = 0
        self.block_reward = 50  # Награда за блок
        self.halving_interval = 210000  # Халвинг каждые 210,000 блоков
        self.blocks_mined = 0

    def create_genesis_block(self):
        return Block(0, "0", time.time(), "Budcoin Genesis Block: Launched May 25, 2025")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        if self.current_supply >= self.max_supply:
            print("Максимальное предложение достигнуто!")
            return
        block = Block(len(self.chain), self.get_latest_block().hash, time.time(), data)
        self.mine_block(block)
        self.chain.append(block)
        self.blocks_mined += 1
        self.current_supply += self.block_reward
        # Халвинг: уменьшение награды каждые 210,000 блоков
        if self.blocks_mined % self.halving_interval == 0:
            self.block_reward /= 2
        print(f"Добыт блок #{block.index}, Награда: {self.block_reward} BDC, Текущий запас: {self.current_supply} BDC")

    def mine_block(self, block):
        while block.hash[:self.difficulty] != "0" * self.difficulty:
            block.nonce += 1
            block.hash = block.calculate_hash()
        print(f"Блок #{block.index} добыт! Хэш: {block.hash}")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

# Запуск Budcoin
if __name__ == "__main__":
    budcoin = Budcoin()
    print("Запуск Budcoin (#BDC)...")
    budcoin.add_block({"transaction": "Alice sends 100 BDC to Bob"})
    budcoin.add_block({"transaction": "Bob sends 50 BDC to Charlie"})
    print(f"Цепочка валидна: {budcoin.is_chain_valid()}")
    print(f"Добыто блоков: {len(budcoin.chain)}, Общий запас: {budcoin.current_supply} BDC")