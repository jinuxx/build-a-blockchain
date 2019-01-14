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
    def new_transaction(self, sender, recipient, amount):
        """
        创建一个记录并加入链中
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