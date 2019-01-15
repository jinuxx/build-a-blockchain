# coding: utf-8
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # 创建起源块
        self.new_block(proof=100, previous_hash=1)

        self.nodes = set()

    def register_node(self, address):
        """
        向节点列表中添加一个新的节点
        :param address: <str> 新节点地址. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        判断入参链是否有效
        :param chain: <list> 一个区块链
        :return: <bool> 是否有效
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # 判断区块的hash是否正确
            if block['previous_hash'] != self.hash(last_block):
                return False

            # 判断工作量证明是否正确
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        这个就是我们的共识机制算法
        将我们的链替换为网络上最长的链来解决冲突
        :return: <bool> 链是否被替换
        """

        neighbours = self.nodes
        new_chain = None

        # 我们之寻找链长度大于自己的
        max_length = len(self.chain)

        # 从网络上查询所有节点的链
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # 判断长度是否比我们长，链是否有效
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # 如果有比我们长且有效的链，则替换我们的链
        if new_chain:
            self.chain = new_chain
            return True

        return False

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
            'sender': sender,
            'recipient': recipient,
            'amount': amount
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


# 初始化节点
app = Flask(__name__)
# 实现返回值中文
app.config['JSON_AS_ASCII'] = False

# 为此节点生成一个唯一的地址
node_identifier = str(uuid4()).replace('-', '')

# 实例化区块链
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # 通过PoW算法计算下一个证明...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 为找到一个证明获得回报
    # 发送者是“0”，表示这个节点已经挖到了一个币
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # 创建一个新的区块并添加到链中
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "新区块已经被创建",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # 检查必填字段
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 创建一个新的记录
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'此记录将被添加的区块位置是： {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "错误：请提供有效的节点列表", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': '已添加新节点',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': '我们的链被替换',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': '我们的链最有权威',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
