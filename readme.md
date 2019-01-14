# [Learn Blockchains by Building One](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46)
The fastest way to learn how Blockchains work is to build one


## 开始之前
区块链(blockchain)是一个不可改变(immutable)、连续(sequential)的链，链内记录着称为区块的元素。其中可以包含记录(transactions)、文件或者任何你想添加的数据，真的！不过，这些区块都是通过 `hashes` 链在一起的。

如果你不懂 `hash` 是什么，[这里有示例](https://learncryptography.com/hash-functions/what-are-hash-functions)。

**准备工作：** 基础 `python` 编写和 `http` 请求。

本文使用 `python3.6+` 和 `pip`，你还要安装 `Flask` 和 `Requests`:
> pip install Flask==0.12.2 requests==2.18.4

**最终代码：** [github](https://github.com/dvf/blockchain)

## 第一步：创建一个区块链

打开你的IDE，创建一个名为 `blockchain.py` 的文件，我们只用一个文件，如果你跟不上，你可以直接看[源码](https://github.com/dvf/blockchain)

### Representing a Blockchain

我们将会创建一个 `Blockchain` 类，这个类的构造方法创建了空的列表(chain)来存储我们的区块链，另一个空的列表(current_transactions)来存储记录(transactions)。

```python
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        # 创建一个区块并加入链中
        pass

    def new_transaction(self, sender, recipient, amount):
        # 创建一个记录并加入链中
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

这个 `Blockchain` 类用来管理区块，存储记录并且有一些协助新增区块到链的方法。现在我们来扩展这些方法，

### 一个区块是什么样子？

每个区块都有一个 `index`，一个 `timestamp`， 一个记录(*transactions*)的列表，一个证明(*proof*，之后我们会讨论)和上一个区块的 `hash`。

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

### 向区块中添加一条记录

我们需要有个方法向区块中添加记录。我们的 `new_transaction()` 方法就是为此而生，而且非常直接。

```python
class Blockchain(object):
    ...

    def new_transaction(self, sender, recipient, amount):
        """
        创建一个记录到下一个被挖掘的(mined)区块中
        :param sender: 发送地址
        :param recipient: 接受地址
        :param amount: 数量
        :return: 这个记录保存的位置
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1
```

在 `new_transaction()` 方法添加了一条记录到列表中后，返回了这个记录将会被添加的到的区块的 `index` —— 也就是下一个会被挖掘(mined)出的区块。在之后这会用来让用户提交记录。

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

在“比特币”中，这个工作量算法称为 [`HashCash`](https://en.wikipedia.org/wiki/Hashcash)，而且这个算法和上面的简单例子里的算法没有什么太大的区别，矿工们通过这个算法竞速来创造新的区块。总的来说，这个算法的难度是由结果字串的长度决定的，矿工们在找到结果后，会收到一个比特币作为回报——in a transaction(以记录的形式)。

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

我们这个类基本结束了，下面我们开始用HTTP request的方式来互动。