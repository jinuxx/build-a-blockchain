# **[Learn Blockchains by Building One](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46)**
The fastest way to learn how Blockchains work is to build one


## 开始之前
区块链(blockchain)是一个不可改变(immutable)、连续(sequential)的链，链内记录着称为区块的元素。其中可以包含交易(transactions)、文件或者任何你想添加的数据，真的！不过，这些区块都是通过 `hashes` 链在一起的。

如果你不懂 `hash` 是什么，[这里有示例](https://learncryptography.com/hash-functions/what-are-hash-functions)。

**准备工作：** 基础 `python` 编写和 `http` 请求。

本文使用 `python3.6+` 和 `pip`，你还要安装 `Flask` 和 `Requests`:
> pip install Flask==0.12.2 requests\==2.18.4

**最终代码：** [github](https://github.com/dvf/blockchain)

## 第一步：创建一个区块链

打开你的IDE，创建一个名为 `blockchain.py` 的文件，我们只用一个文件，如果你跟不上，你可以直接看[源码](https://github.com/dvf/blockchain)

### Representing a Blockchain

我们将会创建一个 `Blockchain` 类，这个类的构造方法创建了空的列表(chain)来存储我们的区块链，另一个空的列表(current_transactions)来存储交易(transactions)。

```python
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        # 创建一个区块并加入链中
        pass

    def new_transaction(self, sender, recipient, amount):
        # 创建一个交易并加入链中
        pass

    @staticmethod
    def hash(self):
        # 计算区块的hash
        pass

    @property
    def last_block(self):
        # 返回链中的最后一个区块
        pass
```

这个 `Blockchain` 类用来管理区块，存储交易并且有一些协助新增区块到链的方法。现在我们来扩展这些方法，

### 一个区块是什么样子？

每个区块都有一个 `index`，一个 `timestamp`， 一个交易(*transactions*)的列表，一个证明(*proof*，之后我们会讨论)和上一个区块的 `hash`。

下面是一个单独的区块的样子：

```js
block = {
    'index': 1,
    'timestamp': 1506057125.900785,
    'transactions': [
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        }
    ],
    'proof': 324984774000,
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
```

到这里，一个 `链` 的样子已经有了——每个区块都包含上一个区块的 `hash`。**这就是区块链有不可变性的原因**：如果有人攻击了前面的区块，那么这个区块后面的所有区块包含的 `hash` 都是错的。

如果你还没明白，花点时间领会一下——这是区块链的核心思想。

### 向区块中添加一条交易

我们需要有个方法向区块中添加交易。我们的 `new_transaction()` 方法就是为此而生，而且非常直接。

```python
class Blockchain(object):
    ...

    def new_transaction(self, sender, recipient, amount):
        """
        创建一个交易到下一个被挖掘的(mined)区块中
        :param sender: 发送地址
        :param recipient: 接受地址
        :param amount: 数量
        :return: 这个交易保存的位置
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1
```

在 `new_transaction()` 方法添加了一条交易到列表中后，返回了这个交易将会被添加的到的区块的 `index` —— 也就是下一个会被挖掘(mined)出的区块。在之后这会用来让用户提交交易。

### 创建新的区块

当我们的 `Blockchain` 实例化后，我们要添加一个“创世(*genesis*)块”，这个区块没有任何前置块。我们也需要给这个“创世块”添加一个“证明(*proof*)”，证明这是挖矿（或者工作量证明）的结果。我们会在后面讨论这个“挖矿(mine)”。

接下来我们扩展 `new_block()`，`new_transaction()` 和 `hash()` 三个方法，在构造器中添加创世块。

```python
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

        # 重置现在的交易列表
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        创建一个交易并加入链中
        :param sender: <str> 发送地址
        :param recipient: <str> 接受地址
        :param amount: <int> 数量
        :return: <int> 保存这个交易的区块链的index
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1
        pass

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
```

上面的代码直截了当——我添加了一些注释来让它更加明了。对于 representing 区块链我们基本已经结束了，但是你一定想要知道新的区块是怎么创建/打造/挖矿挖出的。

### 理解工作量证明(Proof of Work)

工作量证明(*Proof of Work - PoW*)算法——这就是新的区块在区块链中呗创建或者挖出来的算法。PoW算法的最终目标是找出一个结果，一个难以发现却容易证明的数字——从计算方面来说——对于任何一个网络上的人都可以计算出来。这就是工作量证明(*Proof of Work*)算法的核心。

让我们来举一个简单的例子来更好的理解。

让我们来假设某个整数 `x` 乘以另一个整数 `y` 的积的 `hash` 以 `0` 结尾， 也就是 `hash(x * y) = ac23...0` 。对于这个简单的例子，我们把 `x` 的值固定为 `5`，在 `python` 中的实现：

```python
from hashlib import sha256

x = 5
y = 0 # 我们不知道这个y到底是多少

while sha256(f'{x*y}'.encode()).hexdigest()[-1] != "0":
    y += 1

print(f'The solution is y = {y}')
```

这个问题的结果是 `y = 21`，`hash` 的值以 `0` 结尾

> hash(5 * 21) = 1253e9373e...5e3600155e860

在“比特币”中，这个工作量算法称为 [`HashCash`](https://en.wikipedia.org/wiki/Hashcash)，而且这个算法和上面的简单例子里的算法没有什么太大的区别，矿工们通过这个算法竞速来创造新的区块。总的来说，这个算法的难度是由结果字串的长度决定的，矿工们在找到结果后，会收到一个比特币作为回报——in a transaction(以交易的形式)。

网络很容易验证结果的正确性。

### 工作量证明的应用

接下来为我们的区块链实现一个相似的算法，规则会和上面的例子相像。

> 找到一个数字 `proof` , 当和前一区块的结果 **`last_proof`** 一起，凑成 `{proof}{last_proof}` 计算 `hash` 时，结果 `hash` 以4个`0`开头

```python
import hashlib
import json

from time import time
from uuid import uuid4


class Blockchain(object):
    ...
        
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
```

想要调整这个算法难度，可以调整结果要求的开头0的个数，不过4个0最有效率。 你可以看到计算出以1个0开头所需要的时间和4个0所需要的时间简直是天差地别。

**我们这个类基本结束了**，下面我们开始用HTTP请求的方式来互动。

## 第二步：发布区块链为API

接下来我们会用 `Python Flask` 框架来发布API，这样我们就能够用HTTP请求来和区块链交互了。

我们会创建以下方法：

* `/transactions/new` 向区块中添加一个新的交易
* `/mine` 通知服务器去挖掘一个新的区块
* `/chain` 返回整个区块链

### 配置Flask

我们的“服务器”会构造一个单节点的区块链网络，首先是一些模板代码：

```python
import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    ...


# 初始化节点
app = Flask(__name__)

# 为此节点生成一个唯一的地址
node_identifier = str(uuid4()).replace('-', '')

# 实例化区块链
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    return "我们会挖掘一个新的区块"
  
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    return "我们会添加一个新的交易"

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

上面新增代码的简明阐述：

* 15行：实例化节点。更多`Flask`相关请看[这里](http://flask.pocoo.org/docs/0.12/quickstart/#a-minimal-application)
* 18行：为节点创建一个随机的名字
* 21行：实例化`Blockchain`类
* 24-26行：创建 `/mine` 端点，这是个`GET`方法
* 28-30行：创建 `/transactions/new` 端点，这是个`POST`方法，我们之后会发送数据给它
* 32-38行：创建 `/chain` 端点，这是个`GET`方法，返回了整个区块链
* 40-41行：服务器启动在`5000`端口

### 交易的端点 The Transaction Endpoint

下面是一个交易的请求的格式，用户应该按照这个格式发送到服务器：

```json
{
 "sender": "my address",
 "recipient": "someone else's address",
 "amount": 5
}
```

我们已经定义了向区块添加数据交易的方法，所以rest方法很简单，下面我们重写新增交易的方法：

```python

import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

...

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201
```

### 挖掘的端点
我们的挖掘端点简单又神奇，它做了3件事：

1. 计算工作量证明
2. 给矿工回报——以添加一个交易的形式给矿工一个币
3. 创建新的区块并添加到链中

```python
import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

...

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
```

注意，被挖出的区块的接收地址是我们的节点，并且绝大多数的工作只是和我们的区块链类内的方法互动。到这里，我们的工作完成了，接下来该和我们的区块链互动了。

## 第三部：和区块链进行互动

你可以用经典的 `cURL` 或者 `Postman` 来和我们的API进行互动。

让我们启动项目先：

> $ python blockchain.py
>
> \* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

首先我们开始挖掘一个区块，通过调用 `GET` 请求：

> http://localhost:5000/mine

返回值：

```json
{
    "index": 2,
    "message": "新区块已经被创建",
    "previous_hash": "dbbb10f72a569b14856000f72c524bb9c2bc18d120750e4db503486ede7cbfe4",
    "proof": 35293,
    "transactions": [
        {
            "amount": 1,
            "recipient": "cf9f9338d9ab4f35a1d38472d1b00762",
            "sender": "0"
        }
    ]
}
```

然后创建一个新的交易：`post` 调用 `http://localhost:5000/transactions/new` 方法，请求体传入交易的结构：

```json
{
    "amount": 5,
    "recipient": "someone-other-address",
    "sender": "cf9f9338d9ab4f35a1d38472d1b00762"
}
```

返回值：

```json
{
    "message": "此交易将被添加的区块位置是： 3"
}
```

下面我们看下整个链的结构：`GET` 调用 `http://localhost:5000/chain` :

```json
{
    "chain": [
        {
            "index": 1,
            "previous_hash": 1,
            "proof": 100,
            "timestamp": 1547533711.2220762,
            "transactions": []
        },
        {
            "index": 2,
            "previous_hash": "dbbb10f72a569b14856000f72c524bb9c2bc18d120750e4db503486ede7cbfe4",
            "proof": 35293,
            "timestamp": 1547533714.8932798,
            "transactions": [
                {
                    "amount": 1,
                    "recipient": "cf9f9338d9ab4f35a1d38472d1b00762",
                    "sender": "0"
                }
            ]
        }
    ],
    "length": 2
}
```

## 第四步：共识机制（Consensus）

这部分很流弊，我们前面已经实现了一个简单的区块链，这个区块链接收交易并且还可以挖掘新的区块，不过整个区块链的要点是*去中心化*。如果实现了去中心化，我们该怎么保证他们对应的是同一个链呢？这个问题被称为共识机制问题。如果我们的网络中有多个节点，还要实现一个共识机制算法。

### 注册新的节点

在实现共识机制算法之前，我们还需要让一个节点知道网络上周围的节点。网络上的每个节点都要保存一份其他节点的注册信息，因此我们需要更多的端点(endpoint)。

1. `/nodes/register` 来接收URL格式的节点列表
2. `/nodes/resolve` 来实现共识机制算法，这个算法解决了所有的冲突——确定了所有的节点都使用正确的链。

接下来我们要修改 `Blockchain` 类的构造器，并且提供一个方法来注册节点：

```python

...
from urllib.parse import urlparse
...


class Blockchain(object):
    def __init__(self):
        ...
        self.nodes = set()
        ...

    def register_node(self, address):
        """
        向节点列表中添加一个新的节点
        :param address: <str> 新节点地址. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
```

注意，我们用了一个 `set()` 来保存节点，这是最简单并且能够保证在添加新节点时的[幂等性](https://baike.baidu.com/item/%E5%B9%82%E7%AD%89/8600688?fr=aladdin)的方法，这意味着对于一个特定节点，无论添加多少次，在节点列表中只有一次。

### 实现共识机制算法

正如上面所提到的，当一个节点和其他节点所有的链不同，这就是一个冲突。为了解决这个冲突，我们要定制一个规则：即最长有效链是权威链。换句话说，网络上最长的链就是有效的链。通过这个规则，网络上的节点都达成了共识。

```python
...
import requests


class Blockchain(object)
    ...
    
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
```

第一个方法 `valid_chain()` 通过循环判断每个区块，验证 `hash` 和 `proof` 来验证链是否有效。

第二个方法 `resolve_conflicts()` 循环所有的相邻节点，下载他们的链，并且验证。**如果一个有效的链且长度比我们长的链被发现，我们就替换掉自己的**。

下面我们注册两个端点到我们的API中，一个用来添加相邻节点，另一个来解决冲突。

```python
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
```

现在你可以找一台不同的机器，在你的网络上启动不同的节点，或者在同一机器不同端口启动。我在同一机器上启动了两个端口：`http://localhost:5000` 和 `http://localhost:5001`，并且向两个接口中分别注册了对方。

接着我在节点2上挖了一些新的区块，保证它的链更长一点。之后我调用了节点1上的 `GET /nodes/resolve` 方法，接着节点1的链由于共识机制就被替换掉了。

成功！


