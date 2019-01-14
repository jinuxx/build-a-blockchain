# coding: utf-8
import hashlib
import json
from time import time


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # 创建起源块
        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """
        创建一个新的区块
        :param proof: <int> 工作的算法提供的证明
        :param previous_hash: (Optional) <str> 前一个区块的hash
        :return: <dict> 新的区块
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # 重置现在的记录列表
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        创建一个记录并加入链中
        :param sender: <str> 发送地址
        :param recipient: <str> 接受地址
        :param amount: <int> 数量
        :return: <int> 保存这个记录的区块链的index
        """
        self.current_transactions.append({
            sender: sender,
            recipient: recipient,
            amount: amount
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        简单的工作量证明算法 PoW
        找到一个数字 proof , 当和前一区块的结果 last_proof 计算 hash 时，结果 hash 以4个0开头
        :param last_proof: <int> 上一个结果proof
        :return: <int> 结果proof
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        验证hash(last_proof, proof)是否以4个0开头
        :param last_proof: <int> 上一个区块的proof
        :param proof: <int> 现在的proof
        :return: <bool> 是否4个0开头
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        """
        创建入参区块的 SHA-256 值
        :param block: <dict> 区块
        :return: <str>
        """
        # 我们保证区块里的key值是有序的，否则 hashes 会不一致
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
