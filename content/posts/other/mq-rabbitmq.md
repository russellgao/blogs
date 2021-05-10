+++
title = "消息队列原理之rabbitmq"
description = "消息队列原理之rabbitmq"
date = "2020-12-16"
aliases = ["消息队列原理之rabbitmq"]
author = "russellgao"
draft = false
tags = [
    "rabbitmq",
    "消息队列"
]

categories = [
    "mq"
]
+++

## 导读
> 谈起消息队列，我们的脑海可能会不由自主的冒出这么几个关键词，解耦、异步化、消峰、广播等，消息队列的种类也很多，如 rabbitmq、rocketmq、activemq、kafka等还有各个云厂商提供的消息队列。
>它们都有各种的特点和使用场景，所以这个系列的文章主要谈各个消息的原理，目前规划了两篇文章，rabbitmq 和 kafka ，其他的暂时还没有用到，还没有深究。
>
> 这篇主要介绍 rabbitmq 的原理和基于 golang 如何使用。

## 介绍
RabbitMQ 是一个由 Erlang 开发的 AMQP(Advanced Message Queuing Protocol，高级消息队列协议)的开源实现，用于在分布式系统中存储转发消息，在易用性、扩展性、高可用性等方面表现不俗。支持多种客户端语言。

## 架构
> 整体架构对照下面的图说明

![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/rabbitmq-arch.svg)

先看看图片上各个名次的解释: 

- Broker:它提供一种传输服务，它的角色就是维护一条从生产者到消费者的路线，保证数据能按照指定的方式进行传输，简单来说就是消息队列服务器实体。
- Connection: 客户端与 `Rabbitmq Broker` 直接的 `TCP` 连接，通常一个客户端与 Broker 之间只需要一个连接即可。 
- Channel: 消息通道，在客户端的每个连接里，可建立多个channel，最好每个线程都用独立的Channel，后续的对 `Queue` 和 `Exchange` 的操作都是在 Channel 中完成的。
- Producer: 消息生产者，通过和 `Broker` 建立 Connection 和 Channel ，向 Exchange 发送消息。
- Consumer: 消息消费者，通过和 `Broker` 建立 Connection 和 Channel，从 Queue 中消费消息。
- Exchange: 消息交换机，按照一定的策略把 Producer 生产的消息投递到 Queue 中，等待消费者消费。
- Queue: 消息队列载体，每个消息都会被投入到一个或多个队列。
- Vhost: 虚拟主机，一个broker里可以开设多个vhost，用作权限分离，把不同的系统使用的rabbitmq区分开，共用一个消息队列服务器，但看上去就像各自在用不用的rabbitmq服务器一样。
- Binding：绑定，它的作用就是把exchange和queue按照路由规则绑定起来，这样RabbitMQ就知道如何正确地将消息路由到指定的Queue了。
- RoutingKey：路由关键字，生产者在将消息发送给Exchange的时候，一般会指定一个routing key，来指定这个消息的路由规则，而这个routing key需要与Exchange Type及binding key联合使用才能最终生效。

> 这里面比较难理解的概念是 `RoutingKey`,`Exchange`,`Binding` ，消费发送时不会直接发送给 `Queue` ,而是先发送给 `Exchange`，由 `Exchange` 按照一定的规则投递到与它绑定的 `Queue` 中，那这个规则是什么呢?
> 规则就与 `Exchange` 的 Type、`Binding`、`RoutingKey` 相关，`Exchange` 支持的类型有 4 种，`direct,fanout,topic,headers`,含义如下:
>
> - direct: `Queue` 和 `Exchange` 在绑定时需要指定一个 `key`, 我们称为 `Bindkey`。`Producer` 往 `Exchange` 发送消息时，也需要指定一个 `key` ，这个 `key` 就是 `Routekey`。这种模式下 Exchange 会把消息投递给 `Routekey` 和 `Bindkey` 相同的队列
> - fanout: 类似于广播的方式，会把消息投递给和 Exchange 绑定的所有队列，不需要检查 `Routekey` 和 `Bindkey` 。
> - topic: 类似于组播的方式，这种模式下 `Bingkey` 支持模糊匹配，`*` 代表匹配**一个任意词组**，`#`代表匹配**0个或多个词组**。如 Producer 产生一条 RouteKey 为 `benz.car` 的消息，
>同时这个 Exchange 绑定了3组队列（**请注意是3组不是3个，意思是Exchange可以和同一个Queue进行多次绑定，通过Bindkey 的不同，它们之间是多对多的关系**），Bindkey 分别为: `car` ,`*.car` ,`benz.car` ,那么会把这个消息投递到 `*.car`、`benz.car` 对应的 `Queue` 中。
> - headers: 这个类型 `Routekey` 和 `Bindkey` 的匹配规则来路由消息，而是根据发送的消息内容中的 `headers` 属性进行匹配。

对照上面图和名次解释应该比较清晰明了了，下面我们通过几个例子说明如何使用。

## 用法（golang）
### direct
![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/rabbitmq-exchange.jpg)

先看看 Rabbitmq 默认的 exchange ，其中第一个(AMQP default) 是默认的，默认绑定了所有的 `Queue` ，会把消息投递到 Routekey 对应的队列中，即： `Routekey==QueueName` 。
```go
package main

import (
	"fmt"
	"github.com/streadway/amqp"
	"log"
)

func handlerError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

var url = "amqp://username:password@ip:port"

func main() {
	conn, err := amqp.Dial(url)
	handlerError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	channel, err := conn.Channel()
	handlerError(err, "Failed to open a Channel")
	defer channel.Close()

	queueNameCar := "car"
	if _, err := channel.QueueDeclare(queueNameCar, false, false, false, false, nil); err != nil {
		handlerError(err, "Failed to decare Queue")
	}

	if err := channel.Publish("", queueNameCar, false, false, amqp.Publishing{ContentType: "text/plain", Body: []byte("test car")}); err != nil {
		handlerError(err, "Failed to publish message")
	}
}

```

- 这里是一个完整的 Demo， 后面只会提供`main() 函数`的示例代码，其他的和这里这里类似。
- 申明了一个名称为 `car` 的消息队列，并没有做任何的绑定，往 `defalut exchange` 发送一条消息，routekey 为 `car` ,可以看到和队列名相同。
- 为了方便演示，结果以图片的方式展现，可以看到这里有 `car` 的队列，并且有一条消息。
![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/rabbitmq-queue-1.jpg)

> 在创建队列有几个参数可以关注一下 
> ![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/rabbitmq-queue-2.jpg)
> - Durability： 持久化，是否将队列持久化到磁盘，当选择持久化时当 rabbitmq 重启了，这个队列还在，否则当重启了之后这个队列就没有了，需要重新创建，这个需要设计程序时考虑到。
> - Auto delete: 当其中一个消费者已经完成之后，会删除这个队列并断开与其他的消费者的连接。
> - Arguments：
>   - x-message-ttl: 消息的过期时间，发布到队列中的消息在被丢弃之前可以存活多久。
>   - x-expires: 队列的过期时间，一个队列在多长时间内未使用会被自动删除。
>   - x-max-length: 队列的长度，最多剋容纳多少条消息。
>   - x-max-length-bytes: 队列最大可以包含多大的消息。
>   - x-dead-letter-exchange: 当消息过期或者被客户端`reject` 之后应该重新投递到那个`exchange` ，类似与一个`producer`发送消息时选择`exchange`
>   - x-dead-letter-routing-key: 当消息过期或者被客户端`reject` 之后重新投递时的 `Routekey`，类似与一个`producer`发送消息时设置`routekey`，默认是原消息的 `routekey`
>   - x-max-priority: 消息的优先级设置，设置可以支持的最大优先级，如设置为`10`,则可以在发送消息设置优先级，可以根据优先级处理消息，默认为空，当为空时则不支持优先级
>   - x-queue-mode: 将队列设置为懒惰模式，尽可能多地将消息保留在磁盘上，以减少RAM的使用量；如果不设置，队列将保留内存中的缓存，以尽可能快地传递消息。

我们自己创建一个 direct 类型的 exchange 并绑定一些队列看看是什么效果。

```go
func main() {
	conn, err := amqp.Dial(url)
	handlerError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	channel, err := conn.Channel()
	handlerError(err, "Failed to open a Channel")
	defer channel.Close()

	directExchangeNameCar := "direct.car"
	if err := channel.ExchangeDeclare(directExchangeNameCar, "direct", true, false, false, false, nil); err != nil {
		handlerError(err, "Failed to decalare exchange")
	}

	queueNameCar := "car"
	queueNameBigCar := "big-car"
	queueNameMiddleCar := "middle-car"
	queueNameSmallCar := "small-car"
	channel.QueueDeclare(queueNameCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameBigCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameMiddleCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameSmallCar, false, false, false, false, nil)

	if err := channel.QueueBind(queueNameCar, "car", directExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}
	if err := channel.QueueBind(queueNameBigCar, "car", directExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}
	if err := channel.QueueBind(queueNameBigCar, "big.car", directExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}

	if err := channel.QueueBind(queueNameMiddleCar, "car", directExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}
	if err := channel.QueueBind(queueNameMiddleCar, "middler.car", directExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}

	if err := channel.QueueBind(queueNameSmallCar, "car", directExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}
	if err := channel.QueueBind(queueNameSmallCar, "small.car", directExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}

	if err := channel.Publish(directExchangeNameCar, "car", false, false, amqp.Publishing{ContentType: "text/plain", Body: []byte("test car")}); err != nil {
		handlerError(err, "Failed to publish message")
	}
}
```

- 代码中申明了 1 一个 `Exchange` ，4个 `Queue`，7个 `Binding` ,其中一个 `Binding` 详情如下:
    ![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/rabbitmq-queue-4.jpg)
- 可以看到向这个 Exchange 中发消息，Routekey 为 `car` ,匹配的队列有个，那么这4个队列中都应该有消息才对
    ![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/rabbitmq-queue-3.jpg)
    和我们的设想是一直

> `Queue` 的创建上面已经讲过了，这里有 `Exchange` 的创建，那么再看看创建 `Exchange` 有哪些参数
>   ![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/rabbitmq-exchange-1.jpg)
> - Type: 类型，上面已经涉及到了
> - Durability: 持久化
> - Auto delete: 是否自动删除，如果为yes 则当其中队列完成 `unbind` 操作，则其他的 `queue` 或者 `exchange` 也会 unbind 并且删除这个 `exchange` 。
> - Internal: 如果为yes ，则客户端不能直接往这个 exchange 上发送消息，只能用作和 `exchange` 绑定。

### fanout
fanout 工作方式类似于广播，看看下面的代码
```go
func main() {
	conn, err := amqp.Dial(url)
	handlerError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	channel, err := conn.Channel()
	handlerError(err, "Failed to open a Channel")
	defer channel.Close()

	fanoutExchangeNameCar := "fanout.car"
	if err := channel.ExchangeDeclare(fanoutExchangeNameCar, "fanout", true, false, false, false, nil); err != nil {
		handlerError(err, "Failed to decalare exchange")
	}

	queueNameCar := "car"
	queueNameBigCar := "big-car"
	queueNameMiddleCar := "middle-car"
	queueNameSmallCar := "small-car"
	channel.QueueDeclare(queueNameCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameBigCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameMiddleCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameSmallCar, false, false, false, false, nil)

	if err := channel.QueueBind(queueNameCar, "car", fanoutExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}
	if err := channel.QueueBind(queueNameBigCar, "car", fanoutExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}
	if err := channel.QueueBind(queueNameBigCar, "big.car", fanoutExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}

	if err := channel.QueueBind(queueNameMiddleCar, "car", fanoutExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}
	if err := channel.QueueBind(queueNameMiddleCar, "middler.car", fanoutExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}

	if err := channel.QueueBind(queueNameSmallCar, "car", fanoutExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}
	if err := channel.QueueBind(queueNameSmallCar, "small.car", fanoutExchangeNameCar, false, nil); err != nil {
		handlerError(err, "Failed to bind queue to exchange")
	}

	if err := channel.Publish(fanoutExchangeNameCar, "middle.car", false, false, amqp.Publishing{ContentType: "text/plain", Body: []byte("test car")}); err != nil {
		handlerError(err, "Failed to publish message")
	}
}
```

- 这个申明了一个 `fanout` 类型的 exchange ，和上面的代码类似，只有 exchange 不同。
- 可以先在脑海中想想每个 queue 中有几条消息。
- 向 `fanout.car` 这个 exchange 发消息指定 Routekey 为 `middle.car` ，但是由于是广播模式，所以和 routekey 是没有关系的，每个消息队列中各有一条消息。
- 请注意有些 binding 指向的是同一个 queue ，那么会产生多条消息到相同的 queue 中，答案是否定的。producer 产生一条消息，根据一定的规则，每个队列只会收到一条(如何符合投递规则的话)。
    ![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/rabbitmq-queue-5.jpg)

### topic
topic 比较有意思了，和之前的简单粗暴的用法不一样了，先看看下面的代码，声明了一个 `topic` 类型的 `exchange`， 4个 `queue`

```go
func main() {
	conn, err := amqp.Dial(url)
	handlerError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	channel, err := conn.Channel()
	handlerError(err, "Failed to open a Channel")
	defer channel.Close()

	topicExchangeNameCar := "topic.car"
	if err := channel.ExchangeDeclare(topicExchangeNameCar, "topic", true, false, false, false, nil); err != nil {
		handlerError(err, "Failed to decalare exchange")
	}

	queueNameCar := "car"
	queueNameBigCar := "big-car"
	queueNameMiddleCar := "middle-car"
	queueNameSmallCar := "small-car"
	channel.QueueDeclare(queueNameCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameBigCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameMiddleCar, false, false, false, false, nil)
	channel.QueueDeclare(queueNameSmallCar, false, false, false, false, nil)

	if err := channel.QueueBind(queueNameCar, "car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }
    if err := channel.QueueBind(queueNameBigCar, "car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }
    if err := channel.QueueBind(queueNameBigCar, "big.car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }

    if err := channel.QueueBind(queueNameMiddleCar, "car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }
    if err := channel.QueueBind(queueNameMiddleCar, "middler.car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }

    if err := channel.QueueBind(queueNameSmallCar, "car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }
    if err := channel.QueueBind(queueNameSmallCar, "small.car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }
    if err := channel.QueueBind(queueNameSmallCar, "*.small.car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }
    if err := channel.QueueBind(queueNameSmallCar, "#.small.car", topicExchangeNameCar, false, nil); err != nil {
        handlerError(err, "Failed to bind queue to exchange")
    }
}
```

现在思考每个 `producer` 产生消息之后，会有哪些 `queue` 会收到消息。

```go
	if err := channel.Publish(topicExchangeNameCar, "car", false, false, amqp.Publishing{ContentType: "text/plain", Body: []byte("test car")}); err != nil {
		handlerError(err, "Failed to publish message")
	}
```
- 每个 queue 都会收到消息

```go
	if err := channel.Publish(topicExchangeNameCar, "small.car", false, false, amqp.Publishing{ContentType: "text/plain", Body: []byte("test car")}); err != nil {
		handlerError(err, "Failed to publish message")
	}
```
- `small-car` 这一个队列会收到消息。
    - 符合 Routekey 为 `small.car` 、`*.small.car`、`#.small.car` 的binding

```go
	if err := channel.Publish(topicExchangeNameCar, "benz.small.car", false, false, amqp.Publishing{ContentType: "text/plain", Body: []byte("test car")}); err != nil {
		handlerError(err, "Failed to publish message")
	}
```

- `small-car` 这一个队列会收到消息。
    - 符合 Routekey 为 `*.small.car`、`#.small.car` 的binding

```go
	if err := channel.Publish(topicExchangeNameCar, "auto.blue.benz.small.car", false, false, amqp.Publishing{ContentType: "text/plain", Body: []byte("test car")}); err != nil {
		handlerError(err, "Failed to publish message")
	}
```

- `small-car` 这一个队列会收到消息。
    - 符合 Routekey 为 `#.small.car` 的binding

```go
	if err := channel.Publish(topicExchangeNameCar, "bike", false, false, amqp.Publishing{ContentType: "text/plain", Body: []byte("test car")}); err != nil {
		handlerError(err, "Failed to publish message")
	}
```
- 都不会收到消息，没有符合的 routekey 。

### headers 
这种类型很少有实际的应用场景。

## 参考
- https://www.rabbitmq.com/documentation.html
