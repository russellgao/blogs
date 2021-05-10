+++
title = "Python 中的装饰器"
description = "Python 中的装饰器"
date = "2021-01-30 10:32:00"
aliases = ["Python 中的装饰器"]
author = "russellgao"
draft = false
tags = [
    "python",
    "装饰器"
,]

categories = [
    "python"
]

+++

## 导读
>这篇文章主要介绍了 python 当中的装饰器。
>

## 什么是装饰器
装饰器可以理解为函数的函数，想想这么一种场景，要计算每个函数的执行时间，一种解决方法是在每个函数中做个计时，就可以拿到执行时间，
但是这样会有大量的冗余代码，显然是不可取的，这时候装饰器就派上用场了。

下面直接看代码，代码比文字更有说服力。

## 装饰器有哪些类型
### 无参装饰器
装饰器本身没有任务参数，通过 `@` 直接使用即可。

```python
import time
from datetime import datetime

def timet(func) :
    print("otter=====")
    def inner(*args, **kwargs) :
        start_time = datetime.now()
        print("inner====")
        func(*args, **kwargs)
        end_time = datetime.now()
        print("total cost {}".format(end_time - start_time))
    return inner

@timet
def p_p1(a1,a2,a3 = "pkfjf") :
    print("=====")
    print(a1)
    print(a2)
    print(a3)
    print("======")
    time.sleep(4)

p_p1("a1111111","a22222")
```

### 有参装饰器
装饰器本身还有参数，在使用时可以传参控制。

```python
import time
from datetime import datetime


def timet(*args, **kwargs) :
    print("装饰器参数 =====")
    for item_a in args :
        print(item_a)
    for item_k ,item_v in kwargs.items() :
        print(item_k,item_v)
    print("装饰器参数------")

    def outter(func) :
        print("otter=====")
        def inner(*args, **kwargs) :
            start_time = datetime.now()
            print("inner====")
            func(*args, **kwargs)
            end_time = datetime.now()
            print("total cost {}".format(end_time - start_time))
        return inner
    return outter

@timet("p1","p2",p3="oirei",p4="uryhd")
def p_p1(a1,a2,a3 = "pkfjf") :
    print("=====")
    print(a1)
    print(a2)
    print(a3)
    print("======")
    time.sleep(4)

p_p1("a1111111","a22222")
```


