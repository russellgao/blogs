# 消息队列原理之kafka


## 导读
> 本文消息队列系列第二篇，上一篇讲述的是 [Rabbitmq](https://russellgao.cn/mq-rabbitmq/) ，这篇主要介绍 `Kafka` 的原理与使用。
>
>Kafka 是一个快速、可扩展的、高吞吐的、可容错的分布式“发布-订阅”消息系统， 使用 Scala 与 Java 语言编写，能够将消息从一个端点传递到另一个端点。
>较之传统的消息中间件（例如 ActiveMQ、RabbitMQ），Kafka 具有高吞吐量、内置分区、支持消息副本和高容错的特性，非常适合大规模消息处理应用程序。
> 
>Kafka 官网：`http://kafka.apache.org/`

## Kafka 主要设计目标如下
- 以时间复杂度为 O(1) 的方式提供消息持久化能力，即使对 TB 级以上数据也能保证常数时间的访问性能。
- 高吞吐率。即使在非常廉价的商用机器上也能做到单机支持每秒 100K 条消息的传输。
- 支持 Kafka Server 间的消息分区，及分布式消费，同时保证每个 Partition 内的消息顺序传输。
- 同时支持离线数据处理和实时数据处理。
- 支持在线水平扩展。

## Kafka 通常用于两大类应用程序
- 建立实时流数据管道，以可靠地在系统或应用程序之间获取数据。
- 构建实时流应用程序，以转换或响应数据流。

要了解 Kafka 如何执行这些操作，让我们从头开始深入研究 Kafka 的功能。

## 首先几个概念
- Kafka 在一个或多个可以跨越多个数据中心的服务器上作为集群运行。
- Kafka 集群将记录流存储在称为主题的类别中。
- 每个记录由一个键，一个值和一个时间戳组成。

## Kafka 架构体系如下图
![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/kafka-1.png)

Kafka 的应用场景非常多, 下面我们就来举几个我们最常见的场景：

- 用户的活动跟踪：用户在网站的不同活动消息发布到不同的主题中心，然后可以对这些消息进行实时监测、实时处理。当然，也可以加载到 Hadoop 或离线处理数据仓库，对用户进行画像。像淘宝、天猫、京东这些大型电商平台，用户的所有活动都要进行追踪的。
- 日志收集如下图：

    ![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/kafka-2.png)
    
- 限流削峰如下图：

    ![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/kafka-3.png)
    
    高吞吐率实现：Kafka 与其他 MQ 相比，最大的特点就是高吞吐率。为了增加存储能力，Kafka 将所有的消息都写入到了低速大容量的硬盘。按理说，这将导致性能损失，但实际上，Kafka 仍然可以保持超高的吞吐率，并且其性能并未受到影响。

其主要采用如下方式实现了高吞吐率：

- 顺序读写：Kafka 将消息写入到了分区 Partition 中，而分区中的消息又是顺序读写的。顺序读写要快于随机读写。
- 零拷贝：生产者、消费者对于 Kafka 中的消息是采用零拷贝实现的。
- 批量发送：Kafka 允许批量发送模式。
- 消息压缩：Kafka 允许对消息集合进行压缩。

## Kafka 的优点
- 解耦：在项目启动之初来预测将来项目会碰到什么需求，是极其困难的。消息系统在处理过程中间插入了一个隐含的、基于数据的接口层，两边的处理过程都要实现这一接口。这允许你独立的扩展或修改两边的处理过程，只要确保它们遵守同样的接口约束。
- 冗余（副本）：有些情况下，处理数据的过程会失败。除非数据被持久化，否则将造成丢失。消息队列把数据进行持久化直到它们已经被完全处理，通过这一方式规避了数据丢失风险。许多消息队列所采用的"插入-获取-删除"范式中，在把一个消息从队列中删除之前，需要你的处理系统明确的指出该消息已经被处理完毕，从而确保你的数据被安全的保存直到你使用完毕。
- 扩展性：因为消息队列解耦了你的处理过程，所以增大消息入队和处理的频率是很容易的，只要另外增加处理过程即可。不需要改变代码、不需要调节参数。扩展就像调大电力按钮一样简单。
- 灵活性&峰值处理能力：在访问量剧增的情况下，应用仍然需要继续发挥作用，但是这样的突发流量并不常见；如果为以能处理这类峰值访问为标准来投入资源随时待命无疑是巨大的浪费。使用消息队列能够使关键组件顶住突发的访问压力，而不会因为突发的超负荷的请求而完全崩溃。
- 可恢复性：系统的一部分组件失效时，不会影响到整个系统。消息队列降低了进程间的耦合度，所以即使一个处理消息的进程挂掉，加入队列中的消息仍然可以在系统恢复后被处理。
- 顺序保证：在大多使用场景下，数据处理的顺序都很重要。大部分消息队列本来就是排序的，并且能保证数据会按照特定的顺序来处理。Kafka 保证一个 Partition 内的消息的有序性。
- 缓冲：在任何重要的系统中，都会有需要不同的处理时间的元素。例如，加载一张图片比应用过滤器花费更少的时间。消息队列通过一个缓冲层来帮助任务最高效率的执行，写入队列的处理会尽可能的快速。该缓冲有助于控制和优化数据流经过系统的速度。
- 异步通信：很多时候，用户不想也不需要立即处理消息。消息队列提供了异步处理机制，允许用户把一个消息放入队列，但并不立即处理它。想向队列中放入多少消息就放多少，然后在需要的时候再去处理它们。

## Kafka 与其他 MQ 对比
- RabbitMQ：RabbitMQ 是使用 Erlang 编写的一个开源的消息队列，本身支持很多的协议：AMQP，XMPP，SMTP，STOMP，也正因如此，它非常重量级，更适合于企业级的开发。同时实现了 Broker 构架，这意味着消息在发送给客户端时先在中心队列排队。对路由，负载均衡或者数据持久化都有很好的支持。
- Redis：Redis 是一个基于 Key-Value 对的 NoSQL 数据库，开发维护很活跃。虽然它是一个 Key-Value 数据库存储系统，但它本身支持 MQ 功能，所以完全可以当做一个轻量级的队列服务来使用。对于 RabbitMQ 和 Redis 的入队和出队操作，各执行 100 万次，每 10 万次记录一次执行时间。测试数据分为 128Bytes、512Bytes、1K 和 10K 四个不同大小的数据。实验表明：入队时，当数据比较小时 Redis 的性能要高于 RabbitMQ，而如果数据大小超过了 10K，Redis 则慢的无法忍受；出队时，无论数据大小，Redis 都表现出非常好的性能，而 RabbitMQ 的出队性能则远低于 Redis。
- ZeroMQ：ZeroMQ 号称最快的消息队列系统，尤其针对大吞吐量的需求场景。ZeroMQ 能够实现 RabbitMQ 不擅长的高级/复杂的队列，但是开发人员需要自己组合多种技术框架，技术上的复杂度是对这 MQ 能够应用成功的挑战。ZeroMQ 具有一个独特的非中间件的模式，你不需要安装和运行一个消息服务器或中间件，因为你的应用程序将扮演这个服务器角色。你只需要简单的引用 ZeroMQ 程序库，可以使用 NuGet 安装，然后你就可以愉快的在应用程序之间发送消息了。但是 ZeroMQ 仅提供非持久性的队列，也就是说如果宕机，数据将会丢失。其中，Twitter 的 Storm 0.9.0 以前的版本中默认使用 ZeroMQ 作为数据流的传输（Storm 从 0.9 版本开始同时支持 ZeroMQ 和 Netty 作为传输模块）。
- ActiveMQ：ActiveMQ 是 Apache 下的一个子项目。类似于 ZeroMQ，它能够以代理人和点对点的技术实现队列。同时类似于 RabbitMQ，它少量代码就可以高效地实现高级应用场景。
- Kafka/Jafka：Kafka 是 Apache 下的一个子项目，是一个高性能跨语言分布式发布/订阅消息队列系统，而 Jafka 是在 Kafka 之上孵化而来的，即 Kafka 的一个升级版。

Kafka 具有以下特性:

- 快速持久化，可以在 O(1) 的系统开销下进行消息持久化。
- 高吞吐，在一台普通的服务器上既可以达到 10W/s 的吞吐速率。
- 完全的分布式系统，Broker、Producer、Consumer 都原生自动支持分布式，自动实现负载均衡。
- 支持 Hadoop 数据并行加载，对于像 Hadoop 的一样的日志数据和离线分析系统，但又要求实时处理的限制，这是一个可行的解决方案。

Kafka 通过 Hadoop 的并行加载机制统一了在线和离线的消息处理。Apache Kafka 相对于 ActiveMQ 是一个非常轻量级的消息系统，除了性能非常好之外，还是一个工作良好的分布式系统。

Kafka 的几种重要角色如下：

- Kafka 作为存储系统：任何允许发布与使用无关的消息发布的消息队列都有效地充当了运行中消息的存储系统。Kafka 的不同之处在于它是一个非常好的存储系统。写入 Kafka 的数据将写入磁盘并进行复制以实现容错功能。Kafka 允许生产者等待确认，以便直到完全复制并确保即使写入服务器失败的情况下写入也不会完成。

    Kafka 的磁盘结构可以很好地扩展使用-无论服务器上有 50KB 还是 50TB 的持久数据，Kafka 都将执行相同的操作。由于认真对待存储并允许客户端控制其读取位置，因此您可以将 Kafka 视为一种专用于高性能，低延迟提交日志存储，复制和传播的专用分布式文件系统。

- Kafka 作为消息传递系统：Kafka 的流概念与传统的企业消息传递系统相比如何？传统上，消息传递具有两种模型：排队和发布订阅。在队列中，一组使用者可以从服务器中读取内容，并且每条记录都将转到其中一个。在发布-订阅记录中广播给所有消费者。这两个模型中的每一个都有优点和缺点。排队的优势在于，它允许您将数据处理划分到多个使用者实例上，从而扩展处理量。

    不幸的是，队列不是多用户的—一次进程读取了丢失的数据。发布-订阅允许您将数据广播到多个进程，但是由于每条消息都传递给每个订阅者，因此无法扩展处理。Kafka 的消费者群体概念概括了这两个概念。与队列一样，使用者组允许您将处理划分为一组进程（使用者组的成员）。与发布订阅一样，Kafka 允许您将消息广播到多个消费者组。

    Kafka 模型的优点在于，每个主题都具有这些属性-可以扩展处理范围，并且是多订阅者，无需选择其中一个。与传统的消息传递系统相比，Kafka 还具有更强的订购保证。传统队列将记录按顺序保留在服务器上，如果多个使用者从队列中消费，则服务器将按记录的存储顺序分发记录。但是，尽管服务器按顺序分发记录，但是这些记录是异步传递给使用者的，因此它们可能在不同的使用者上乱序到达。

    这实际上意味着在并行使用的情况下会丢失记录的顺序。消息传递系统通常通过“专有使用者”的概念来解决此问题，该概念仅允许一个进程从队列中使用，但是，这当然意味着在处理中没有并行性。Kafka 做得更好，通过在主题内具有并行性（即分区）的概念，Kafka 能够在用户进程池中提供排序保证和负载均衡。

    这是通过将主题中的分区分配给消费者组中的消费者来实现的，以便每个分区都由组中的一个消费者完全消费。通过这样做，我们确保使用者是该分区的唯一读取器，并按顺序使用数据。由于存在许多分区，因此仍然可以平衡许多使用者实例上的负载。但是请注意，使用者组中的使用者实例不能超过分区。

- Kafka 用作流处理：仅读取，写入和存储数据流是不够的，目的是实现对流的实时处理。在 Kafka 中，流处理器是指从输入主题中获取连续数据流，对该输入进行一些处理并生成连续数据流以输出主题的任何东西。例如，零售应用程序可以接受销售和装运的输入流，并输出根据此数据计算出的重新订购和价格调整流。

    可以直接使用生产者和消费者 API 进行简单处理。但是，对于更复杂的转换，Kafka 提供了完全集成的 Streams API。这允许构建执行非重要处理的应用程序，这些应用程序计算流的聚合或将流连接在一起。该功能有助于解决此类应用程序所面临的难题：处理无序数据，在代码更改时重新处理输入，执行状态计算等。
    
    流 API 建立在 Kafka 提供的核心原语之上：它使用生产者和使用者 API 进行输入，使用 Kafka 进行状态存储，并使用相同的组机制来实现流处理器实例之间的容错。

## Kafka 中的关键术语解释
**Topic：** 主题。在 Kafka 中，使用一个类别属性来划分消息的所属类，划分消息的这个类称为 Topic。Topic 相当于消息的分类标签，是一个逻辑概念。物理上不同 Topic 的消息分开存储，逻辑上一个 Topic 的消息虽然保存于一个或多个 Broker 上但用户只需指定消息的 Topic 即可生产或消费数据而不必关心数据存于何处。

**Partition：** 分区。Topic 中的消息被分割为一个或多个 Partition，其是一个物理概念，对应到系统上 就是一个或若干个目录。Partition 内部的消息是有序的，但 Partition 间的消息是无序的。

**Segment 段:** 将  Partition 进一步细分为了若干的 Segment，每个 Segment 文件的大小相等。

**Broker：** Kafka 集群包含一个或多个服务器，每个服务器节点称为一个 Broker。Broker 存储 Topic 的数据。如果某 Topic 有 N 个 Partition，集群有 N 个 Broker，那么每个 Broker 存储该 Topic 的一个 Partition。

如果某 Topic 有 N 个 Partition，集群有（N+M）个 Broker，那么其中有 N 个 Broker 存储该 Topic 的一个 Partition，剩下的 M 个 Broker 不存储该 Topic 的 Partition 数据。如果某 Topic 有 N 个 Partition，集群中 Broker 数目少于 N 个，那么一个 Broker 存储该 Topic 的一个或多个 Partition。在实际生产环境中，尽量避免这种情况的发生，这种情况容易导致 Kafka 集群数据不均衡。

**Producer：** 生产者。即消息的发布者，生产者将数据发布到他们选择的主题。生产者负责选择将哪个记录分配给主题中的哪个分区。即：生产者生产的一条消息，会被写入到某一个 Partition。

**Consumer：** 消费者。可以从 Broker 中读取消息。一个消费者可以消费多个 Topic 的消息；一个消费者可以消费同一个 Topic 中的多个 Partition 中的消息；一个 Partiton 允许多个 Consumer 同时消费。

**Consumer Group：** Consumer Group 是 Kafka 提供的可扩展且具有容错性的消费者机制。组内可以有多个消费者，它们共享一个公共的 ID，即 Group ID。组内的所有消费者协调在一起来消费订阅主题 的所有分区。Kafka 保证同一个 Consumer Group 中只有一个 Consumer 会消费某条消息。

实际上，Kafka 保证的是稳定状态下每一个 Consumer 实例只会消费某一个或多个特定的 Partition，而某个 Partition 的数据只会被某一个特定的 Consumer 实例所消费。

下面我们用官网的一张图, 来标识 Consumer 数量和 Partition 数量的对应关系。

![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/kafka-4.jpg)

由两台服务器组成的 Kafka 群集，其中包含四个带有两个使用者组的分区（P0-P3）。消费者组 A 有两个消费者实例，组 B 有四个。


对于这个消费组, 以前一直搞不明白, 我自己的总结是：Topic 中的 Partitoin 到 Group 是发布订阅的通信方式。


即一条 Topic 的 Partition 的消息会被所有的 Group 消费，属于一对多模式；Group 到 Consumer 是点对点通信方式，属于一对一模式。

举个例子：不使用 Group 的话，启动 10 个 Consumer 消费一个 Topic，这 10 个 Consumer 都能得到 Topic 的所有数据，相当于这个 Topic 中的任一条消息被消费 10 次。

使用 Group 的话，连接时带上 groupid，Topic 的消息会分发到 10 个 Consumer 上，每条消息只被消费 1 次。

**Replizcas of partition：** 分区副本。副本是一个分区的备份，是为了防止消息丢失而创建的分区的备份。

**Partition Leader：** 每个 Partition 有多个副本，其中有且仅有一个作为 Leader，Leader 是当前负责消息读写 的 Partition。即所有读写操作只能发生于 Leader 分区上。

**Partition Follower：** 所有 Follower 都需要从 Leader 同步消息，Follower 与 Leader 始终保持消息同步。Leader 与 Follower 的关系是主备关系，而非主从关系。

**ISR：**

- **ISR，In-Sync Replicas**，是指副本同步列表。ISR 列表是由 Leader 负责维护。
- **AR，Assigned Replicas**，指某个 Partition 的所有副本, 即已分配的副本列表。
- **OSR，Outof-Sync Replicas**，即非同步的副本列表。
- **AR=ISR+OSR**


**Offset：** 偏移量。每条消息都有一个当前 Partition 下唯一的 64 字节的 Offset，它是相当于当前分区第一条消息的偏移量。

**Broker Controller：** Kafka集群的多个 Broker 中，有一个会被选举 Controller，负责管理整个集群中 Partition 和 Replicas 的状态。

只有 Broker Controller 会向 Zookeeper 中注册 Watcher，其他 Broker 及分区无需注册。即 Zookeeper 仅需监听 Broker Controller 的状态变化即可。

HW 与 LEO：

- **HW，HighWatermark，高水位**，表示 Consumer 可以消费到的最高 Partition 偏移量。HW 保证了 Kafka 集群中消息的一致性。确切地说，是保证了 Partition 的 Follower 与 Leader 间数 据的一致性。
- **LEO，Log End Offset**，日志最后消息的偏移量。消息是被写入到 Kafka 的日志文件中的， 这是当前最后一个写入的消息在 Partition 中的偏移量。
- 对于 Leader 新写入的消息，Consumer 是不能立刻消费的。Leader 会等待该消息被所有 ISR 中的 Partition Follower 同步后才会更新 HW，此时消息才能被 Consumer 消费。

我相信你看完上面的概念还是懵逼的，好吧！下面我们就用图来形象话的表示两者的关系吧：

![](https://gitee.com/russellgao/blogs-image/raw/master/images/mq/kafka-6.png)

**Zookeeper：** Zookeeper 负责维护和协调 Broker，负责 Broker Controller 的选举。在 Kafka 0.9 之前版本，Offset 是由 ZK 负责管理的。

总结：ZK 负责 Controller 的选举，Controller 负责 Leader 的选举。

**Coordinator：** 一般指的是运行在每个 Broker 上的 Group Coordinator 进程，用于管理 Consumer Group 中的各个成员，主要用于 Offset 位移管理和 Rebalance。一个 Coordinator 可以同时管理多个消费者组。


**Rebalance：** 当消费者组中的数量发生变化，或者 Topic 中的 Partition 数量发生了变化时，Partition 的所有权会在消费者间转移，即 Partition 会重新分配，这个过程称为再均衡 Rebalance。

再均衡能够给消费者组及 Broker 带来高性能、高可用性和伸缩，但在再均衡期间消费者是无法读取消息的，即整个 Broker 集群有小一段时间是不可用的。因此要避免不必要的再均衡。

**Offset Commit：** Consumer 从 Broker 中取一批消息写入 Buffer 进行消费，在规定的时间内消费完消息后，会自动将其消费消息的 Offset 提交给 Broker，以记录下哪些消息是消费过的。当然，若在时限内没有消费完毕，其是不会提交 Offset 的。

## Kafka的工作原理和过程
### 消息写入算法
消息发送者将消息发送给 Broker, 并形成最终的可供消费者消费的 log，是比较复杂的过程：

- Producer 先从 Zookeeper 中找到该 Partition 的 Leader。
- Producer将消息发送给该 Leader。
- Leader 将消息接入本地的 log，并通知 ISR 的 Followers。
- ISR 中的 Followers 从 Leader 中 Pull 消息, 写入本地 log 后向 Leader 发送 Ack。
- Leader 收到所有 ISR 中的 Followers 的 Ack 后，增加 HW 并向 Producer 发送 Ack，表示消息写入成功。

### 消息路由策略
在通过 API 方式发布消息时，生产者是以 Record 为消息进行发布的。

Record 中包含 Key 与 Value，Value 才是我们真正的消息本身，而 Key 用于路由消息所要存放的 Partition。


消息要写入到哪个 Partition 并不是随机的，而是有路由策略的：

- 若指定了 Partition，则直接写入到指定的 Partition。
- 若未指定 Partition 但指定了 Key，则通过对 Key 的 Hash 值与 Partition 数量取模，该取模。
- 结果就是要选出的 Partition 索引。
- 若 Partition 和 Key 都未指定，则使用轮询算法选出一个 Partition。

### HW 截断机制
如果 Partition Leader 接收到了新的消息， ISR 中其它 Follower 正在同步过程中，还未同步完毕时 leader 宕机。

此时就需要选举出新的 Leader。若没有 HW 截断机制，将会导致 Partition 中 Leader 与 Follower 数据的不一致。

当原 Leader 宕机后又恢复时，将其 LEO 回退到其宕机时的 HW，然后再与新的 Leader 进行数据同步，这样就可以保证老 Leader 与新 Leader 中数据一致了，这种机制称为 HW 截断机制。

### 消息发送的可靠性
生产者向 Kafka 发送消息时，可以选择需要的可靠性级别。通过 request.required.acks 参数的值进行设置。
**0 值：** 异步发送。生产者向 Kafka 发送消息而不需要 Kafka 反馈成功 Ack。该方式效率最高，但可靠性最低。

>- 其可能会存在消息丢失的情况：
>- 在传输过程中会出现消息丢失。
>- 在 Broker 内部会出现消息丢失。

会出现写入到 Kafka 中的消息的顺序与生产顺序不一致的情况。


**1 值：** 同步发送。生产者发送消息给 Kafka，Broker 的 Partition Leader 在收到消息后马上发送成功 Ack（无需等等 ISR 中的 Follower 同步）。


生产者收到后知道消息发送成功，然后会再发送消息。如果一直未收到 Kafka 的 Ack，则生产者会认为消息发送失败，会重发消息。

该方式对于 Producer 来说，若没有收到 Ack，一定可以确认消息发送失败了，然后可以重发。

但是，即使收到了 ACK，也不能保证消息一定就发送成功了。故，这种情况，也可能会发生消息丢失的情况。


**-1 值：** 同步发送。生产者发送消息给 Kafka，Kafka 收到消息后要等到 ISR 列表中的所有副本都 同步消息完成后，才向生产者发送成功 Ack。


如果一直未收到 Kafka 的 Ack，则认为消息发送 失败，会自动重发消息。该方式会出现消息重复接收的情况。

## 参考
本文系转载 [https://mp.weixin.qq.com/s/R1en4V0Tlwlpt102BjotoA](https://mp.weixin.qq.com/s/R1en4V0Tlwlpt102BjotoA)
