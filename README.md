markdown

# Budcoin (#BDC)

![Budcoin Logo](images/budcoin-logo.png)

**Budcoin** is a symbol of a new global balance, inspired by the eternal cycle of Samsara. In a world where money is a tool of greed, power, and inequality, Budcoin offers a different path: a path of mindful value distribution, driven not by fear or greed, but by experience and compassion. The distribution of wealth should be a result of wisdom. Like the Wheel of Samsara, each rebirth is determined by past actions. This is a digital Dharma—a currency that reflects inner growth, not just external accumulation. Budcoin is not about profit. It is a tool for a new balance. A world measured not only by numbers but also by consciousness.

- **Total Supply**: 21,000,000 BDC
- **Consensus**: Proof-of-Work (SHA-256)
- **Block Reward**: 50 BDC (halves every 210,000 blocks)
- **Halving**: Every 210,000 blocks

## Blockchain and P2P Network
Budcoin is a true blockchain with Proof-of-Work (PoW):
- **PoW Difficulty**: Block hash must start with "000000".
- **Transaction Support**: Transfer BDC between addresses.
- **Halving**: Block reward halves every 210,000 blocks.
- **Decentralized Network**: Nodes synchronize the chain via P2P.

## Installation
### Requirements
- Python 3.6 or higher
- Standard Python libraries: `json`, `hashlib`, `socket`, `threading` (included with Python)
- Operating System: Linux, macOS, or Windows

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Buddhacoin/Budcoin.git
   cd Budcoin

- **Run a node:**

bash

python3 Budcoin.py 5000

- **(Optional) Connect to another node:**

bash

python3 Budcoin.py 5001 127.0.0.1 5000

### Usage

**Running a Node:** Start a node to participate in mining and blockchain synchronization.

**Mining:** Each block includes a reward (50 BDC initially, with halving every 210,000 blocks).

**Transactions:** Create transactions programmatically using the create_transaction(sender, receiver, amount) method.

**Check Balance:** Use the get_balance(address) method to view an address's balance.

**P2P Network:** Nodes automatically sync with peers to maintain the latest blockchain state.

### Examples
**Start the first node:**
   
bash

python3 Budcoin.py 5000

**Start a second node and connect to the first:**

bash

python3 Budcoin.py 5001 127.0.0.1 5000

