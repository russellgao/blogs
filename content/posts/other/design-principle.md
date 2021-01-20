+++
title = "设计模式六大原则"
description = "设计模式六大原则"
date = "2021-01-19"
aliases = ["设计模式六大原则"]
author = "russellgao"
draft = false
tags = [
    "设计模式"
]
+++

## 导读
> 重温设计模式的原则
>

## 六大原则
### 单一职责原则
> There should never be more than one reason for a class to change.
>
> 就一个类而言， 应该仅有一个引起它变化的原因。

### 开放封闭原则
> Software entities like classes,modules and functions should be open for extension but closed for modifications.
>
> 类、模块、函数等应该是可以拓展的，但是不可修改。

开闭原则指导我们，当软件需要变化时，应该尽量通过拓展的方式来实现变化，而不是通过修改已有代码来实现。这里的“应该尽量”4个字说明OCP原则并不是说绝对不可以修改原始类的。当我们嗅到原来的代码“腐化气味”时，应该尽早地重构，以便使代码恢复到正常的“进化”过程，而不是通过集成等方式添加新的实现，这会导致类型的膨胀以及历史遗留代码的冗余。因此，在开发过程中需要自己结合具体情况进行考量，是通过修改旧代码还是通过继承使得软件系统更稳定、更灵活，在保证去除“代码腐化”的同时，也保证原有模块的正确性。

### 里式替换原则
> Functions that use pointers or references to base classes must be able to use objects of derived classes without knowing it.
>
> 所有引用基类的地方必须能透明地使用其子类的对象。

里氏替换原则的核心原理是抽象，抽象又依赖于继承这个特性，在OOP中，继承的优缺点相当明显，有点如下：

- 代码重用，减少创建类成本，每个子类拥有父类的属性和方法；
- 子类和父类基本相似，但又与父类有所区别；
- 提高代码的可拓展性。

继承的缺点：

- 继承是侵入性的，只要继承就必须拥有父类的所有属性和方法；
- 可能造成子类代码的冗余、灵活性降低，因为子类必须拥有弗雷的属性和方法。

开闭原则和里氏替换原则往往是生死相依、不离不弃的，通过里氏替换来达到对扩展的开发，对修改的关闭效果。


### 迪米特原则(最少知识原则)
> Only talk to you immediate friends.
>
> 一个软件实体应当尽可能少地与其他实体发生相互作用。

### 接口隔离原则
> The dependency of one class to another one should depend on the smallest possible interface.
>
> 一个类对另一个类的依赖应该建立在最小的接口上。

建立单一接口，不要建立庞大臃肿接口；尽量细化接口，接口中方法尽量少。也就是说，我们要为各个类建立专用的接口，而不要试图建立一个很庞大的接口供所有依赖它的类调用。

- 接口尽量小，但是要有限度。对接口进行细化可以提高程序设计的灵活性；但是如果过小，则会造成接口数量过多，使设计复杂化。所以，一定要适度。
- 为依赖接口的类定制服务，只暴露给调用的类需要的方法，它不需要的方法则隐蔽起来。只有专注得为一个模块提供定制服务，才能建立最小的依赖关系。
- 提高内聚，减少对外交互。接口方法尽量少用public修饰。接口是对外的承诺，承诺越少对系统开发越有利，变更风险也会越少。



### 依赖倒置原则
> High level modules should not depends upon low level modules.Both should depend upon abstractions.Abstractions should not depend upon details.Details should depend upon abstractions.
>
> 高层模块不应该依赖于低层模块，两者都应该依赖于抽象。抽象不应该依赖于细节，细节应该依赖于抽象。


## 总结
- 单一职责原则告诉我们实现类要职责单一
- 里氏替换原则告诉我们不要破坏继承体系
- 依赖倒置原则告诉我们要面向接口编程
- 接口隔离原则告诉我们在设计接口的时候要精简单一
- 迪米特法则告诉我们要降低耦合。
- 开闭原则是总纲，告诉我们要对扩展开放，对修改关闭。
