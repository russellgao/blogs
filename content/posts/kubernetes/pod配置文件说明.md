+++
title = "pod 配置文件说明"
description = "pod 配置文件说明"
date = "2020-06-18"
aliases = ["elk on k8s"]
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "pod"
,]

categories = [
    "kubernetes"
]

+++

## Pod的定义文件
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: string
  namaspace: string
  labels:
  - name: string
  annotations:
  - name: string
spec:
  containers:
  - name: string
    # 使用的镜像
    image: string
    imagePullPolicy: [Always | Never | IfNotPresent]
    command: [string]
    args: [string]
    # 工作目录
    workingDir: string
    volumeMounts:
    - name: string
      mountPath: string
      readOnly: boolean
    ports:
    - name: string
      containerPort: int
      hostPort: int
      protocol: string
    env:
    - name: string
      value: string
    resources:
      limits:
        cpu: string
        memory: string
      requests:
        cpu: string
        memory: string
    livenessProbe:
      exec:
        command: [string]
      httpGet:
        path: string
        port: int
        host: string
        scheme: string
        httpHeaders:
        - name: string
          value: string
      tcpSocket:
        port: int
      # 多久之后去检查
      initialDelaySeconds: number
      # 健康检查超时时间
      timeoutSeconds: number
      # 多长时间检查一次
      periodSeconds: number
      # 成功的阀值，检查几次成功才算成功
      successThreshold: 0
      # 失败的阀值，检查几次失败才算失败
      failureThreshold: 0
    securityContext:
    # 详细参见 pod_SecurityContext 章节
    # securityContext 可以配置pod 或者container 级别
      runAsUser: 1000
    # 运行的用户
      runAsGroup: 3000
    # 运行的用户组
      fsGroup: 2000
      privileged: bool
    # 是否以privileged 权限运行，即这是这个进程拥有特权
      allowPrivilegeEscalation: bool
    # 控制一个进程是否能比其父进程获取更多的权限，如果一个容器以privileged权限运行或具有CAP_SYS_ADMIN权限，则AllowPrivilegeEscalation的值将总是true
      capabilities:
        add: ["NET_ADMIN", "SYS_TIME","..."]
    # 给某个特定的进程privileged权限，而不用给root用户所有的privileged权限
    terminationMessagePath: /dev/termination-log
    # 容器终止的日志文件
    terminationMessagePolicy: [File | FallbackToLogsOnError]
    # 默认为File, 容器终止消息输出到文件
  restartPolicy: [Always | Never | OnFailure]
# 重启策略，默认为 Always
  nodeSelector: object
# 通过label 选取node
  dnsPolicy: ClusterFirst
# pod 的 dns 策略 ,可以配置如下值
# Default : 和宿主机的DNS完全一致
# ClusterFirst: 把集群的DNS写入到Pod的DNS配置，但是如果设置了HostNetwork=true，就会强制设置为Default
# ClusterFirstWithHostNet: 把集群的DNS写入到Pod的DNS配置，不管是否设置HostNetwork
# None: 忽略所有的DNS配置，一般来说，设置了None之后会自己手动再设置dnsConfig
  enableServiceLinks: true
# Kubernetes支持两种查找服务的主要模式: 环境变量和DNS, 如果不需要服务环境变量, 将 `enableServiceLinks` 标志设置为 `false` 来禁用此模式
  terminationGracePeriodSeconds: 10
# 发出删除pod指令后多久之后真正的删除pod
  serviceAccountName: jenkins
# pod 绑定的serviceAccount
  priorityClassName:
# 给pod 设置优先级，参考 : https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/
  schedulerName: default-scheduler
# 如果不配置则使用kubernetes 默认的default-scheduler，如果这个不满足要求则可以自定义一个scheduler
# https://kubernetes.io/zh/docs/tasks/administer-cluster/configure-multiple-schedulers/
  affinity:
# 亲和性设置
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
# 容忍设置
  imagePullSecrets:
  - name: string
# 镜像拉取策略
  hostNetwork: false
# 是否使用主机网络，默认为false，如果为true，pod直接用主机网络，在pod中可以看到主机的网络接口
  volumes:
  - name: string
    emptyDir: {}
    hostPath:
      path: string
    secret:
      secretName: string
      items:
      - key: string
        path: string
    configMap:
      name: string
      items:
      - key: string
        path: string
# 目录挂载

```

## pod 具体的样例
```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: elastic-cluster
  name: enode-0
spec:
  containers:
  - env:
    - name: ES_JAVA_OPTS
      valueFrom:
        configMapKeyRef:
          key: ES_JAVA_OPTS
          name: es-config
    image: elasticsearch:6.7.2
    imagePullPolicy: IfNotPresent
    livenessProbe:
      failureThreshold: 3
      httpGet:
        path: /_cluster/health?local=true
        port: 9200
        scheme: HTTP
      periodSeconds: 600
      successThreshold: 1
      timeoutSeconds: 1
    name: elasticsearch
    ports:
    - containerPort: 9200
      name: es-http
      protocol: TCP
    - containerPort: 9300
      name: es-transport
      protocol: TCP
    readinessProbe:
      failureThreshold: 3
      httpGet:
        path: /_cluster/health?local=true
        port: 9200
        scheme: HTTP
      initialDelaySeconds: 30
      periodSeconds: 20
      successThreshold: 1
      timeoutSeconds: 1
    resources:
      limits:
        cpu: "2"
        memory: 10Gi
      requests:
        cpu: "1"
        memory: 8Gi
    securityContext:
      capabilities:
        add:
        - IPC_LOCK
        - SYS_RESOURCE
      privileged: true
      runAsUser: 1000
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /usr/share/elasticsearch/data
      name: es-data
    - mountPath: /usr/share/elasticsearch/logs
      name: es-logs
    - mountPath: /usr/share/elasticsearch/config/elasticsearch.yml
      name: elasticsearch-config
      subPath: elasticsearch.yml
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-k4r6f
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: true
  hostname: enode-0
  initContainers:
  - command:
    - sysctl
    - -w
    - vm.max_map_count=262144
    image: busybox
    imagePullPolicy: IfNotPresent
    name: init-sysctl
    resources: {}
    securityContext:
      privileged: true
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-k4r6f
      readOnly: true
  priority: 0
  restartPolicy: Always
  schedulerName: default-scheduler
  securityContext:
    fsGroup: 1000
  serviceAccount: default
  serviceAccountName: default
  subdomain: elasticsearch-cluster
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - name: es-data
    persistentVolumeClaim:
      claimName: es-data-enode-0
  - name: es-logs
    persistentVolumeClaim:
      claimName: es-logs-enode-0
  - configMap:
      defaultMode: 420
      items:
      - key: elasticsearch.yml
        path: elasticsearch.yml
      name: es-config
    name: elasticsearch-config
  - name: default-token-k4r6f
    secret:
      defaultMode: 420
      secretName: default-token-k4r6f
```


