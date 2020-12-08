# Python 中的迭代器与生成器


## 导读
这篇文章主要介绍了 python 当中的迭代器与生成器，在涉及到大数量的场景应该考虑使用迭代器与生成器。

## 可迭代对象
如果一个对象实现了 `__iter__` 方法，那么我们就称它是一个可迭代对象。如果没有实现 `__iter__` 而实现了
`__getitem__` 方法，并且其参数是从0开始索引的，这种对象也是可迭代的，比如说序列。

使用 `iter` 内置函数可以获取迭代器的对象，当解释器需要迭代对象时，会自动调用 `item(x)` ：

- 如果对象实现了 `__iter__` 方法，获取一个迭代器
- 如果没有实现 `__iter__` ，但是实现了 `__getitem__` ，python 会创建一个迭代器，尝试从索引0开始获取元素
- 如果获取失败，则抛出 `TypeError`

标准序列都实现了 `__iter__` 方法，所以标准序列都是可迭代对象。如 list,dict,set,tuple。

>- 只有实现了 `__iter__` 方法的对象能通过子类测试`issubclass(Object,abc.Itertor)`
>- 检查对象能否迭代最标准的方法是调用 `iter()` 函数，因为 `iter()` 会考虑到实现 `__getitem__` 方法的部分可迭代对象。

## 迭代器
迭代器主要用于从集合中取出元素，那么是什么迭代器呢?

> 实现了 `next` 方法的可迭代对象就是迭代器。

- `next` 返回下一个可用的元素，当没有元素时抛出 `StopIteration` 异常。
- `__iter__` ，迭代器本身。

到这里应该可以看出「可迭代对象」与 「迭代器」的区别了，就是在于有没有实现`next` 方法 。

检查对象是不是一个迭代器 ：`isinstance(object,abc.Iterator)` 。

### 迭代器模式
>按需一次获取一个数据项。

迭代器模式的用途有：

- 访问一个聚合对象而无需暴露它的内部结构
- 支持对聚合对象的多种遍历
- 为遍历不同的聚合结构提供一个统一的接口

说了这么多，那么除了标准序列之外，如何自定义一个迭代器呢，看看下面的代码：

```python
class Books:
    def __init__(self, books):
        self.books = books.split(",")

    def __iter__(self):
        return BookIterator(self.books)


class BookIterator:
    def __init__(self, books):
        self.books = books
        self.index = 0

    def next(self):
        try :
            book = self.books[self.index]
        except IndexError:
            raise StopIteration()
        self.index += 1
        return book

    def __iter__(self):
        return self

books = Books("python,golang,vue,kubernetes,istio")
print(books)
for book in books :
    print(book)
```

## 生成器
生成器是一种特殊的迭代器，这种迭代器更加优雅，不需要像上面一样写 `__iter__` 和 `next` 方法了，只需要一个 `yield` 关键字即可。



生成器有两种方法用:

- yield
- `()` 生成

### yield

```python
def gen(x) :
    for i in range(x) :
        yield i * 2

g1 = gen(10)
```

### () 生成器
```python
l1 = [ i * 2 for i in range(10) ]
g1 = (i * 2 for i in range(10))

for i in g1 :
    print(i)

print(l1)
```

- l1 是一个列表推导式
- g1 是一个生成器
- 两者的区别是 g1 生成器采用懒加载的方式，不会一次把数据加载到内存中

> 生成器的好处不用把数据全部加载到内存中，访问到的时候在计算出来。例如有 100w 的数据集，但是只需要访问前 100 个，是不是生成器就很有用了。


## 总结
>- 任何对象只要实现了 `__iter__` 方法就是一个可迭代对象
>- 任何对象只要实现了 `__iter__` 和 `next` 方法就是一个迭代器
>- 生成器是一个特殊的迭代器，可以通过 `yield` 和 `()` 的方式生成
>- 在数据量大的时候使用会有奇效
