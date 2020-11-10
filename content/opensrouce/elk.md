+++
title = "istio中的ELK实践"
description = "投稿到 servicemesh 社区的文章"
date = "2020-11-10"
aliases = ["about-me"]
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "istio"
,]
+++

# ELK
> 这篇文档是由我投稿的云原生社区的文章，节选自 [istio-handbook](https://www.servicemesher.com/istio-handbook/)，如果有兴趣可以参考这本书。

ELK 指的是由 Elasticsearch + Logstash + Kibana 组成的日志采集、存储、展示为一体的日志解决方案，简称 "ELK Stack"。ELK Stack 还包含 Beats（如Filebeat、Metricbeat、Heartbeat等）、Kafka等成员，是目前主流的一种日志解决方案。

- Elasticsearch 是个开源分布式搜索引擎，提供搜集、分析、存储数据三大功能。
- Logstash 是免费且开放的服务器端数据处理管道，能够从多个来源采集数据，转换数据，然后将数据发送到您最喜欢的“存储库”中。Logstash 比较耗资源，在实践中我们一般用作实时解析和转换数据。Logstash 采用可插拔框架，拥有 200 多个插件。您可以将不同的输入选择、过滤器和输出选择混合搭配、精心安排，让它们在管道中和谐地运行。
- Kibana 是一个开源和免费的工具，Kibana可以为 Logstash 和 ElasticSearch 提供的日志分析友好的 Web 界面，可以帮助汇总、分析和搜索重要数据日志。
- Kafka 是由 Apache 软件基金会开发的一个开源流处理平台，由 Scala 和 Java 编写。用来做缓冲，当日志量比较大的时候可以缓解后端 Elasticsearch 的压力。 
- Beats 是数据采集的得力工具。Beats家族成员包括如下： 
    - Filebeat：用于日志文件采集，内置了多种模块（Apache、Cisco ASA、Microsoft Azure、NGINX、MySQL 等等）。
    - Metricbeat： 用于指标采集。
    - Packetbeat：用于网络数据采集。
    - Winlogbeat：用于Windows 事件采集。
    - Auditbeat：用于审计日志采集。
    - Heartbeat：用于运行时间采集。
    
    **其中 Filebeat 被经常用来收集 Node 或者 Pod 中的日志**。

Beats 用于收集客户端的日志，发送给缓存队列如Kafka，目的是为了解耦数据收集与解析入库的过程，同时提高了可扩展性，使日志系统有峰值处理能力，不会因为突发的访问压力造成日志系统奔溃。缓存队列可选的还有 Redis，由于 Redis 是内存型，很容易写满，生产环境建议用 kafka。Logstash 从 缓存队列中消费日志解析处理之后写到 Elasticsearch，通过 Kibana 展示给最终用户。

## 采集方案
Filebeat 有两种部署模式，一是通过 DaemonSet 方式部署，二是通过 Sidecar 方式部署，Filebeat 采集后发送到 Kafka ，再由 Logstash 从 Kafka 中消费写到 Elasticsearch。

### DaemonSet 方式部署
开启 Envoy 的访问日志输出到 `stdout` ，以 DaemonSet 的方式在每一台集群节点部署 Filebeat ，并将日志目录挂载至 Filebeat Pod，实现对 Envoy 访问日志的采集。

![ELK 日志收集架构 DeamonSet](https://gitee.com/russellgao/blogs-image/raw/master/images/opensource/elk-filebeat-daemonset.png)

### Sidecar 方式部署
Filebeat 和 Envoy 部署在同一个 Pod 内，共享日志数据卷， Envoy 写，Filebeat 读，实现对 Envoy 访问日志的采集。

![ELK 日志收集架构 Sidecar](https://gitee.com/russellgao/blogs-image/raw/master/images/opensource/elk-filebeat-sidecar.png)

## 部署 ELK
有了以上的基础，我们开始部署 `ELK Stack`

### 部署 Kafka
首先，创建一个新的 namespace 用于部署 `ELK Stack`：
```
# Logging Namespace. All below are a part of this namespace.
apiVersion: v1
kind: Namespace
metadata:
  name: logging
```

接下来，部署 Kafka 服务。 Kafka 通过 Zookeeper 管理集群配置，所以在部署 Kafka 需要先部署 Zookeeper。

Zookeeper 是一个分布式的，开放源码的分布式应用程序协调服务。

Kafka 与 Zookeeper 都是有状态服务，部署时需要选择 `StatefulSet` 。

1. 部署 Zookeeper Service
    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: zookeeper-cluster
      namespace: logging
    spec:
      selector:
        app: zookeeper-cluster
      ports:
        - name: http
          port: 2181
          targetPort: 2181
      type: ClusterIP
    ```
   * Zookeeper 在集群内使用，供 Kafka 使用，创建类型为 ClusterIP 的 Service 。
   * Zookeeper 的默认端口是`2181`。

2. 部署 Zookeeper ConfigMap
    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: zookeeper-config
      namespace: logging
    data:
      ZOO_CONF_DIR: /conf
      ZOO_PORT: "2181"
    ```
   * Zookeeper 配置文件中的 key 都可以 以 `ZOO_` 加大写的方式设置到环境变量中，使之生效。
   * 这里仅列举部分配置。

3. 部署 Zookeeper StatefulSet 
    ```yaml
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: zookeeper
     namespace: logging
   spec:
     serviceName: zookeeper-cluster
     replicas: 1
     updateStrategy:
       type: RollingUpdate
     selector:
       matchLabels:
         app: zookeeper-cluster
     template:
       metadata:
         labels:
           app: zookeeper-cluster
         annotations:
           sidecar.istio.io/inject: "false"
       spec:
         containers:
           - name: zookeeper
             resources:
               requests:
                 cpu: 10m
                 memory: 100Mi
               limits:
                 memory: 200Mi
             image: zookeeper
             imagePullPolicy: IfNotPresent
             envFrom:
               - configMapRef:
                   name: zookeeper-config
             readinessProbe:
               tcpSocket:
                 port: 2181
               initialDelaySeconds: 5
               periodSeconds: 10
             livenessProbe:
               tcpSocket:
                 port: 2181
               initialDelaySeconds: 15
               periodSeconds: 20
             ports:
               - containerPort: 2181
                 name: zk-client
    ```
  * sidecar.istio.io/inject=false 标识此服务无需 sidecar 注入。

4. 部署 Kafka Service
    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: bootstrap-kafka
      namespace: logging
    spec:
      clusterIP: None
      ports:
      - port: 9092
      selector:
        app: kafka
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: kafka-cluster
      namespace: logging
    spec:
      ports:
      - name: http
        targetPort: 9092
        port: 9092
      selector:
        app: kafka
      type: ClusterIP
    ```
   * 部署两个 Service 。
       - bootstrap-kafka 为后续部署 Kafka Statefulset 使用。
       - kafka-cluster 为 Kafka 的访问入口，在生产中使用可以用其他的 Service 类型。
       - kafka 的默认端口是`9092`

5. 部署 Kafka ConfigMap

    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: kafka-config
      namespace: logging
    data:
      KAFKA_ADVERTISED_LISTENERS: "PLAINTEXT://kafka-cluster:9092"
      KAFKA_LISTENERS: "PLAINTEXT://0.0.0.0:9092"
      KAFKA_ZOOKEEPER_CONNECT: "zookeeper-cluster:2181"
      KAFKA_LOG_RETENTION_HOURS: "48"
      KAFKA_NUM_PARTITIONS: "30"
    ```
   * Kafka 配置文件（server.properties）中的 key 都可以 以 `KAFKA_` 加大写的方式设置到环境变量中，使之生效。
   * KAFKA_ADVERTISED_LISTENERS 为 Kafka 监听的服务地址。
   * KAFKA_ZOOKEEPER_CONNECT 为前面部署的 Zookeeper 的服务地址。
   * KAFKA_LOG_RETENTION_HOURS 为 Kafka 数据保留的时间，超过这个时间将会被清理，可以根据实际情况进行调整。
   * KAFKA_NUM_PARTITIONS 为创建 Kafka topic 时的默认分片数，设置大一些可以增加 Kafka 的吞吐量。
   * 这里仅列举部分配置。

6. 部署 Kafka StatefulSet
    ```yaml
    apiVersion: apps/v1
    kind: StatefulSet
    metadata:
      name: kafka
      namespace: logging
    spec:
      selector:
        matchLabels:
          app: kafka
      serviceName: bootstrap-kafka
      replicas: 1
      template:
        metadata:
          labels:
            app: kafka
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          containers:
          - name: kafka-broker
            image: russellgao/kafka:2.12-2.0.1
            ports:
            - name: inside
              containerPort: 9092
            resources:
              requests:
                cpu: 0.1
                memory: 1024Mi
              limits:
                memory: 3069Mi
            readinessProbe:
              tcpSocket:
                port: 9092
              timeoutSeconds: 1
              initialDelaySeconds: 5
              periodSeconds: 10
            livenessProbe:
              tcpSocket:
                port: 9092
              timeoutSeconds: 1
              initialDelaySeconds: 15
              periodSeconds: 20
            envFrom:
            - configMapRef:
                name: kafka-config
    ```
   * kafka 对磁盘的 IO 要求较高，可以选择固态硬盘或者经过IO优化的磁盘，否则可能会成为日志系统的瓶颈。

请注意，本次实践没有把数据卷映射出来，在生产实践中使用 `volumeClaimTemplates` 来为 Pod 提供持久化存储。`resources` 可以根据实际情况调整。

### 部署 Logstash
Logstash 是一个无状态服务，通过 Deployment 进行部署。

1. 部署 Logstash ConfigMap

    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: logstash-conf
      namespace: logging
    data:
      logstash.conf: |
        input {
            http {
                host => "0.0.0.0" # default: 0.0.0.0
                port => 8080 # default: 8080
                user => "logstash"
                password => "aoDJ0JVgkfNPjarn"
                response_headers => {
                    "Content-Type" => "text/plain"
                    "Access-Control-Allow-Origin" => "*"
                    "Access-Control-Allow-Methods" => "GET, POST, DELETE, PUT"
                    "Access-Control-Allow-Headers" => "authorization, content-type"
                    "Access-Control-Allow-Credentials" => true
                }
            }
            kafka  {
                topics => "istio"
                bootstrap_servers => "kafka-cluster:9092"
                auto_offset_reset => "earliest"
                group_id => "istio_kafka_gr"
                consumer_threads => 3
                codec => "json"
            }
        }
        filter {
          grok {
                match => { "message" => "(?m)\[%{TIMESTAMP_ISO8601:timestamp}\] "%{NOTSPACE:method} %{NOTSPACE:path} %{NOTSPACE:protocol}" %{NUMBER:response_code:int} %{NOTSPACE:response_flags} "%{NOTSPACE:istio_policy_status}" "%{NOTSPACE:upstream_transport_failure_reason}" %{NUMBER:bytes_received:int} %{NUMBER:bytes_sent:int} %{NUMBER:duration:int} %{NUMBER:upstream_service_time:int} "%{NOTSPACE:x_forwarded_for}" "%{NOTSPACE:user_agent}" "%{NOTSPACE:request_id}" "%{NOTSPACE:authority}" "%{NOTSPACE:upstream_host}" %{NOTSPACE:upstream_cluster} %{NOTSPACE:upstream_local_address} %{NOTSPACE:downstream_local_address} %{NOTSPACE:downstream_remote_address} %{NOTSPACE:requested_server_name} %{NOTSPACE:route_name}" }
                remove_field => ["message"]
          }
          date {
                match => ["timestamp", "yyyy-MM-ddTHH:mm:ss.SSSZ"]
                timezone => "Asia/Shanghai"
          }
          ruby {
              code => "event.set('[@metadata][index_day]',(event.get('@timestamp').time.localtime + 8*60*60 ).strftime('%Y.%m.%d'))"
          }
        }
        output {
            if "_grokparsefailure" not in [tags] {
                elasticsearch {
                    user => "elastic"
                    password => "elastic"
                    hosts => ["elasticsearch.com:9200"]
                    index => "istio-%{[@metadata][index_day]}"
                }
            }
        }
    ```
   Logstash 配置由3部分组成：
   
   **input**
   * Logstash input 支持非常多的数据源，如 File、Elasticsearch、Beats、Redis、Kafka、Http等。
   * Http input 用于Logstash 的健康检查，也可通过 http 接口将日志直接发送到 Logstash，主要用于移动端的场景。
   * Kafka input 用于收集日志，一个input只能从一个 Topic 中读取数据，需要和后续的 Filebeat output 对应。
   
   **filter**
   * Logstash filter 支持非常多的插件，可以对数据进行解析、加工、转换，如 grok、date、ruby、json、drop等。
   * grok 用于对日志进行解析。
   * date 用于把 `timestamp` 转化成 elasticsearch 中的 `@timestamp` 字段，可以指定时区。
   * ruby 插件支持执行 ruby 代码，可以进行复杂逻辑的处理，此处的用法是 `@timestamp` 字段的时间加8小时，解决自动生成的索引时差问题。
      
   **output**
   * Logstash output 支持非常多的数据源，如 elasticsearch、cvs、jdbc 等。
   * 此处是把 grok 解析成功的日志写到 elasticsearch 。

2. 部署 Logstash Deployment

    ```yaml
    apiVersion: apps/v1beta2
    kind: Deployment
    metadata:
      name: logstash
      namespace: logging
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: logstash
      template:
        metadata:
          labels:
            app: logstash
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          volumes:
          - name: config
            configMap:
              name: logstash-conf
          hostname: logstash
          containers:
            - name: logstash
              image: logstash:7.2.0
              args: [
                "-f","/usr/share/logstash/pipeline/logstash.conf",
              ]
              imagePullPolicy: IfNotPresent
              volumeMounts:
              - name: config
                mountPath: "/usr/share/logstash/pipeline/logstash.conf"
                readOnly: true
                subPath: logstash.conf
              resources:
                requests:
                  cpu: 0.5
                  memory: 1024Mi
                limits:
                  cpu: 1.5
                  memory: 3072Mi
              readinessProbe:
                tcpSocket:
                  port: 8080
                initialDelaySeconds: 5
                periodSeconds: 10
              livenessProbe:
                tcpSocket:
                  port: 8080
                initialDelaySeconds: 15
                periodSeconds: 20
    ```
   * Logstash 不需要对外发布服务，即不需要创建 Service，从 Kafka 中消费日志，处理完成之后写到 Elasticsearch 。
   * Logstash 只需要把配置文件挂载进去，无需挂载其他目录，排查错误时可通过 Logstash Console Log 进行查看。

3. 部署 Logstash HorizontalPodAutoscaler

    ```yaml
    apiVersion: autoscaling/v2beta1
    kind: HorizontalPodAutoscaler
    metadata:
      name: logstash
      namespace: logging
    spec:
      scaleTargetRef:
        apiVersion: apps/v1beta2
        kind: Deployment
        name: logstash
      minReplicas: 2
      maxReplicas: 10
      metrics:
      - type: Resource
        resource:
          name: cpu
          targetAverageUtilization: 80
    ```
   * Logstash 比较消费 CPU ，可以部署 HPA，可以根据日志量动态的扩所容。
   * Logstash 的压力对 CPU 比较敏感，可以只根据 CPU 这一个指标进行 HPA。

Logstash 的配置文件支持if/else条件判断，通过这种方式，一个 Logstash 集群可以支持比较多的日志格式。另外 Logstash 的 grok 语法相对复杂，可以使用 Kibana `Dev Tools` 工具进行调试，如下图：

![ELK grok debug](https://gitee.com/russellgao/blogs-image/raw/master/images/opensource/elk-grok-debug.jpg)

### 部署 Filebeat
这里仅给出 Filebeat DaemonSet 的部署过程。

1. 部署 Filebeat ConfigMap

    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: filebeat-conf
      namespace: logging
    data:
      filebeat.yml: |
        filebeat:
          inputs:
            -
              paths:
                - /var/log
                - /var/lib/docker/containers
              ignore_older: 1h
              force_close_files: true #强制filebeat在文件名改变时，关闭文件，会有丢失日志的风险
              close_older: 1m
              fields_under_root: true
        output:
            kafka:
              enabled: true
              hosts: ["kafka-cluster:9092"]
              topic: "istio"
              version: "2.0.0"
              partition.round_robin:
                reachable_only: false
              worker: 2
              max_retries: 3
              bulk_max_size: 2048
              timeout: 30s
              broker_timeout: 10s
              channel_buffer_size: 256
              keep_alive: 60
              compression: gzip
              max_message_bytes: 1000000
              required_acks: 1
    ```
   * input.paths 代表 Filebeat 监听的日志路径。
   * input.ignore_older 代表日志文件的修改时间超过这个之间，将会忽略，这个在 Filebeat 重启时很有效果，解决重复读取日志的问题。
   * out.kafka.hosts 和之前部署的 Kafka Service 对应。
   * out.kafka.topic 和之前部署的 Logstash ConfigMap 中的 input 对应。

2. 部署 Filebeat DaemonSet
    
    ```yaml
    apiVersion: apps/v1
      kind: DaemonSet
      metadata:
        name: filebeat
        namespace: logging
        labels:
          app: filebeat
      spec:
        selector:
          matchLabels:
            app: filebeat
        template:
          metadata:
            labels:
              app: filebeat
            annotations:
              sidecar.istio.io/inject: "false"
          spec:
            containers:
            - name: filebeat
              image: elastic/filebeat:7.2.0
              imagePullPolicy: IfNotPresent
              volumeMounts:
              - name: config
                mountPath: "/usr/share/filebeat/filebeat.yml"
                readOnly: true
                subPath: filebeat.yml
                - name: varlog
                  mountPath: /var/log
                - name: varlibdockercontainers
                  mountPath: /var/lib/docker/containers
              resources:
                requests:
                  cpu: 0.1
                  memory: 200Mi
                limits:
                  cpu: 0.3
                  memory: 600Mi
            volumes:
            - name: varlog
              hostPath:
                path: /var/log
            - name: varlibdockercontainers
              hostPath:
                path: /var/lib/docker/containers
            - name: config
              configMap:
                name: filebeat-conf
    ```
   * 这里声明了两个 `hostPath` 类型的数据卷，路径为日志存储的路径。
   * 将宿主机的 `/var/log` 和 `/var/lib/docker/containers` 挂载到了 Filebeat Pod 内便于 Filebeat 收集日志。
   * Filebeat 不需要部署 Service 。
   * Filebeat 对资源消耗比较少，可忽略对 Node 的资源消耗。

## 小结
本节为大家介绍了 ELK 的原理和安装部署，以及如何收集日志。

## 参考
* [Beats](https://www.elastic.co/cn/beats/)
* [Logstash](https://www.elastic.co/logstash)
* [Zookeeper](https://hub.docker.com/_/zookeeper)