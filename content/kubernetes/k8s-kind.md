+++
title = "在本地如何玩转kubernetes? - kind"
description = "在本地如何玩转kubernetes? - kind"
date = "2021-02-06"
aliases = ["在本地如何玩转kubernetes? - kind"]
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "kind" ,
]
+++

## 导读
> kubernetes 现在已经走进了大众的视野，很多同学都对此比较好奇，从其他渠道或多或少都了解了一些，但是苦于没有kubernetes环境，不能身临其境的感受，
> 毕竟如果完整搭建一套kubernetes环境是需要资源的。 今天介绍一款工具（**kind**），让大家可以本地也可以构建起 kubernetes 环境，愉快的在本地玩转 kubernetes。
>
> kind 全称 是 kubernetes in docker ，把 kubernetes 控制面的组件全部运行在一个docker 容器中，在本地通过 `127.0.0.1` 进行通信。这种玩法只能在本地体验，
> 不可用于生产环境，特别适用于新人在本地体验、开发 kubernetes 相关组件时在本地进行调试等，如开始 operator 时可以在 kind 进行调试 。
>
> 详细用法可以参考官方文档。

## kind 参考资料
- 官网: https://kind.sigs.k8s.io/
- 官方文档: https://kind.sigs.k8s.io/docs/user/quick-start/
- github : https://github.com/kubernetes-sigs/kind

## 安装
### 有 golang 环境
如果有 golang 环境，可以通过如下命令安装 :
```shell script
GO111MODULE="on" go get sigs.k8s.io/kind@v0.10.0
```

如果下载的比较慢可以设置代理，增加一个环境变量即可: 
```shell script
GOPROXY="https://goproxy.cn"
```

### 无 golang 环境
Linux :
```shell script
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.10.0/kind-linux-amd64
chmod +x ./kind
mv ./kind /some-dir-in-your-PATH/kind
```

Mac (homebrew)
```shell script
brew install kind
```

或者 :
```shell script
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.10.0/kind-darwin-amd64

```

Windows:
```shell script
curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.10.0/kind-windows-amd64
Move-Item .\kind-windows-amd64.exe c:\some-dir-in-your-PATH\kind.exe
```

## 基本命令
通过 `kind --help ` 看看支持哪些命令
```shell script
kind --help 
kind creates and manages local Kubernetes clusters using Docker container 'nodes'

Usage:
  kind [command]

Available Commands:
  build       Build one of [node-image]
  completion  Output shell completion code for the specified shell (bash, zsh or fish)
  create      Creates one of [cluster]
  delete      Deletes one of [cluster]
  export      Exports one of [kubeconfig, logs]
  get         Gets one of [clusters, nodes, kubeconfig]
  help        Help about any command
  load        Loads images into nodes
  version     Prints the kind CLI version

Flags:
  -h, --help              help for kind
      --loglevel string   DEPRECATED: see -v instead
  -q, --quiet             silence all stderr output
  -v, --verbosity int32   info log verbosity
      --version           version for kind

Use "kind [command] --help" for more information about a command.
```

可以看出支持3种类型的命令，cluster 相关、image 相关、通用命令 。

- cluster 相关的有 create, delete 等，主要用于创建和删除 kubernetes 集群。
- image 相关的有 build， load 等，主要用于本地调试时，本地可以 build镜像直接load 到集群中，而不需要推送到镜像仓库再通过集群去 pull 。
- 通用命令如 get ，version 等。


kind --version

```shell script
kind --version
kind version 0.9.0
```

本篇文章以 `kind 0.9.0 ` 进行介绍 。下面是比较精彩的部分，仔细看哦 :eyes: 

## 创建 kubernetes 集群
创建一个 kubernetes 集群 ： 

```shell script
kind create cluster
Creating cluster "kind" ...
 ✓ Ensuring node image (kindest/node:v1.19.1) 🖼
 ✓ Preparing nodes 📦  
 ✓ Writing configuration 📜 
 ✓ Starting control-plane 🕹️ 
 ✓ Installing CNI 🔌 
 ✓ Installing StorageClass 💾 
Set kubectl context to "kind-kind"
You can now use your cluster with:

kubectl cluster-info --context kind-kind

Thanks for using kind! 😊
```

一条命令就已经启动好了一个集群 ，可以通过 `kind get clusters` 查看已经创建的集群。
```shell script
kind get clusters
kind
```

既然是 kubernetes in docker ，那就看看启动了哪些容器 :
```shell script
docker ps -a 
CONTAINER ID        IMAGE                                    COMMAND                  CREATED             STATUS              PORTS                                      NAMES
fdb88a476bb0        kindest/node:v1.19.1                     "/usr/local/bin/entr…"   3 minutes ago       Up 2 minutes        127.0.0.1:43111->6443/tcp                  kind-control-plane
```

可以看到有一个控制面的容器启动了，进到容器中看看都有什么
```shell script
[root@iZuf685opgs9oyozju9i2bZ ~]# docker exec -it kind-control-plane bash 
root@kind-control-plane:/# 
root@kind-control-plane:/# 
root@kind-control-plane:/# ps -ef 
UID          PID    PPID  C STIME TTY          TIME CMD
root           1       0  0 02:49 ?        00:00:00 /sbin/init
root         126       1  0 02:49 ?        00:00:00 /lib/systemd/systemd-journald
root         145       1  1 02:49 ?        00:00:06 /usr/local/bin/containerd
root         257       1  0 02:49 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id c1a5e2c868b9a744f4f78a85a8d660950bb76103a38e7
root         271       1  0 02:49 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 3549ecade28e2dccbad5ed15a4cd2b6e6a886cd3e10ab
root         297       1  0 02:49 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 379ed27442f35696d488dd5a63cc61dc474bfa9bd08a9
root         335       1  0 02:49 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id e4eae33bf489c617c7133ada7dbd92129f3f817cb74b7
root         343     271  0 02:49 ?        00:00:00 /pause
root         360     257  0 02:49 ?        00:00:00 /pause
root         365     297  0 02:49 ?        00:00:00 /pause
root         377     335  0 02:49 ?        00:00:00 /pause
root         443     335  0 02:49 ?        00:00:01 kube-scheduler --authentication-kubeconfig=/etc/kubernetes/scheduler.conf --authorization-kubeconfig=/etc/
root         468     297  4 02:49 ?        00:00:17 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --cli
root         496     271  1 02:49 ?        00:00:05 kube-controller-manager --allocate-node-cidrs=true --authentication-kubeconfig=/etc/kubernetes/controller-
root         540     257  1 02:49 ?        00:00:05 etcd --advertise-client-urls=https://172.18.0.2:2379 --cert-file=/etc/kubernetes/pki/etcd/server.crt --cli
root         580       1  1 02:49 ?        00:00:06 /usr/bin/kubelet --bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernete
root         673       1  0 02:50 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id b0965a6f77f58c46cfe7b30dd84ddf4bc37516ba60e6e
root         695     673  0 02:50 ?        00:00:00 /pause
root         709       1  0 02:50 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id aedf0f1fd02baf1cf2b253ad11e33e396d97cc7c53114
root         738     709  0 02:50 ?        00:00:00 /pause
root         789     673  0 02:50 ?        00:00:00 /usr/local/bin/kube-proxy --config=/var/lib/kube-proxy/config.conf --hostname-override=kind-control-plane
root         798     709  0 02:50 ?        00:00:00 /bin/kindnetd
root        1011       1  0 02:50 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id aa554aa998c3091a70eacbc3e4a2f275a1e680a585d69
root        1024       1  0 02:50 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 7373488f811fc5d638c2b3f5f79d953573e30a42ff52f
root        1048       1  0 02:50 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 5ab6c3ef1715623e2c28fbfdecd5f4e6e2616fc20a387
root        1079    1011  0 02:50 ?        00:00:00 /pause
root        1088    1024  0 02:50 ?        00:00:00 /pause
root        1095    1048  0 02:50 ?        00:00:00 /pause
root        1152    1011  0 02:50 ?        00:00:00 /coredns -conf /etc/coredns/Corefile
root        1196    1024  0 02:50 ?        00:00:00 /coredns -conf /etc/coredns/Corefile
root        1205    1048  0 02:50 ?        00:00:00 local-path-provisioner --debug start --helper-image k8s.gcr.io/build-image/debian-base:v2.1.0 --config /et
root        1961       0  0 02:56 pts/1    00:00:00 bash
root        1969    1961  0 02:56 pts/1    00:00:00 ps -ef
root@kind-control-plane:/# 
```

可以看到容器中有很多进程，仔细梳理一下看看有什么组件

- **kube-apiserver ...** : api-server 组件，是操作资源的入口并且提供认证、授权、权限控制、API注册和服务发现的机制
- **kube-scheduler ...** : scheduler 组件，负责资源的调度以及根据预先设定的调度策略将pod调度到合适的节点上
- **kube-controller-manager ...** : controller-manager 组件，负责管理集群的状态，如异常发现、自动扩容和滚动更新等
- **etcd ...** : etcd 组件，主要用于存储 kubernetes 的数据
- **/usr/bin/kubelet ...** : kubelet组件， 负责管理容器的生命周期、数据卷以及网络（CNI）
- **/usr/local/bin/kube-proxy ...** : kube-proxy 组件: 负责服务发现和集群Service的负载均衡
- **/coredns ...** : dns 组件，负责集群内部的域名解析
- **/usr/local/bin/containerd ...** : kubernetes 的 CRI（容器运行时）的具体实现，创建具体 pod 以来这个组件
- **/pause...** : pod 的 根容器，创建 pod 时先创建出这个容器，pod 的网络配置等就是配置到此容器中，后续其他容器会共享这个容器的网络
- **/usr/local/bin/containerd-shim-runc-v2 ...** : 真正的容器，后续启动的pod 都是以这种形式启动

可以看到这个容器中包含了 kubernetes 中所有控制面的组件和数据面的组件，是一个 all in one 的 集群。

这个容器的详细配置可以通过 `docker inspect kind-control-plane ` 查看。

## 使用集群
关于 kubernetes 的使用已经有很多文章来介绍了，所以这里不作为重点介绍，简单演示一下。可以通过 api 或者 kubectl 与kuberntes 进行交互，
这里选择用 kubectl 进行演示。

> 如果本地没有 kubectl 需要进行安装，安装文档参见： https://kubernetes.io/docs/tasks/tools/install-kubectl/
>
> kubectl 的基本用法可以参考我之前的文章 ：[kubectl 常用命令](https://russellgao.cn/kubectl-command/)

以 部署 logstash 为例，我们会创建如下资源 ：

- Namespace 
- Deployment
- Configmap
- Hpa
- Service 

具体的 yaml 文件如下 : 

cat logstash.yaml 
```yaml
---
# setting Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: logging

---
# setting ConfigMap

kind: ConfigMap
apiVersion: v1
metadata:
  name: logstash-conf
  namespace: logging
data:
  logstash.conf: |
    input {
        http {
            host => "0.0.0.0" # default: 0.0.0.0
            port => 8080 # default: 8080
            response_headers => {
                "Content-Type" => "text/plain"
                "Access-Control-Allow-Origin" => "*"
                "Access-Control-Allow-Methods" => "GET, POST, DELETE, PUT"
                "Access-Control-Allow-Headers" => "authorization, content-type"
                "Access-Control-Allow-Credentials" => true
            }
        }
    }
    output {
         stdout {
            codec => rubydebug
        }
    }

---
# setting Depolyment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logstash
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: logstash
  template:
    metadata:
      labels:
        app: logstash
    spec:
      volumes:
      - name: config
        configMap:
          name: logstash-conf
      hostname: logstash
      containers:
        - name: logstash
          image: russellgao/logstash:7.2.0
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
              cpu: 1
              memory: 2048Mi
            limits:
              cpu: 3
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
            timeoutSeconds: 15
      imagePullSecrets:
      - name: harbor

---
apiVersion: autoscaling/v2beta1
kind: HorizontalPodAutoscaler
metadata:
  name: logstash-hpa
  namespace: logging
spec:
  scaleTargetRef:
    apiVersion: apps/v1beta2
    kind: Deployment
    name: logstash
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      targetAverageUtilization: 80

---
apiVersion: v1
kind: Service
metadata:
  name: logstash-custerip
  namespace: logging
spec:
  selector:
    app: logstash
  type: ClusterIP
  ports:
    - name: 'port'
      protocol: TCP
      port: 8080
      targetPort: 8080
```

执行 `kubectl apply -f logstash.yaml` 

```shell script
kubectl apply -f logstash.yaml 
namespace/logging created
configmap/logstash-conf created
deployment.apps/logstash created
horizontalpodautoscaler.autoscaling/logstash-hpa created
service/logstash-custerip created
```

可以看到具体的资源已经被创建出来，下面来观察具体的资源 : 

查看 ConfigMap : 
```shell script
kubectl -n logging get configmap
NAME            DATA   AGE
logstash-conf   1      4m
```

查看 Deployment : 
```shell script
kubectl -n logging get deployment 
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
logstash   1/1     1            1           4m
```

查看 Pod :
```shell script
kubectl -n logging get po -owide
NAME                        READY   STATUS    RESTARTS   AGE   IP           NODE                 NOMINATED NODE   READINESS GATES
logstash-64d58c4b98-nqk4v   1/1     Running   0          93s   10.244.0.9   kind-control-plane   <none>           <none>
```

这里需要注意的是 Pod 所在的 `node` 是 `kind-control-plane` ，而非本机，说明 kubernetes node 就是这个容器，在本地 curl `10.244.0.9:8080` 
这个地址是不通，说明是在集群外， 进到容器内再 curl 就是通的 ：
```shell script
curl 10.244.0.9:8080 -v
* About to connect() to 10.244.0.9 port 8080 (#0)
*   Trying 10.244.0.9...
^C
[root@iZuf685opgs9oyozju9i2bZ k8s]# 
[root@iZuf685opgs9oyozju9i2bZ k8s]# 
[root@iZuf685opgs9oyozju9i2bZ k8s]# docker exec -it kind-control-plane bash 
root@kind-control-plane:/# curl 10.244.0.9:8080 -v 
*   Trying 10.244.0.9:8080...
* TCP_NODELAY set
* Connected to 10.244.0.9 (10.244.0.9) port 8080 (#0)
> GET / HTTP/1.1
> Host: 10.244.0.9:8080
> User-Agent: curl/7.68.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: GET, POST, DELETE, PUT
< Access-Control-Allow-Headers: authorization, content-type
< Access-Control-Allow-Credentials: true
< content-length: 2
< content-type: text/plain
< 
* Connection #0 to host 10.244.0.9 left intact
okroot@kind-control-plane:/# 

```

查看 service :

```shell script
 kubectl -n logging get  svc
NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
logstash-custerip   ClusterIP   10.96.234.144   <none>        8080/TCP   5m
```

pod 和 service 的原理是一样的，通过 `CLUSTER-IP` 访问只能在容器内进行访问。

在 pod 内进行访问
```shell script
[root@iZuf685opgs9oyozju9i2bZ k8s]# kubectl -n logging exec -it logstash-64d58c4b98-nqk4v bash 
bash-4.2$ curl 10.96.234.144:8080 -v
* About to connect() to 10.96.234.144 port 8080 (#0)
*   Trying 10.96.234.144...
* Connected to 10.96.234.144 (10.96.234.144) port 8080 (#0)
> GET / HTTP/1.1
> User-Agent: curl/7.29.0
> Host: 10.96.234.144:8080
> Accept: */*
> 
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: GET, POST, DELETE, PUT
< Access-Control-Allow-Headers: authorization, content-type
< Access-Control-Allow-Credentials: true
< content-length: 2
< content-type: text/plain
< 
* Connection #0 to host 10.96.234.144 left intact
okbash-4.2$
bash-4.2$ curl logstash-custerip:8080 -v
* About to connect() to logstash-custerip port 8080 (#0)
*   Trying 10.96.234.144...
* Connected to logstash-custerip (10.96.234.144) port 8080 (#0)
> GET / HTTP/1.1
> User-Agent: curl/7.29.0
> Host: logstash-custerip:8080
> Accept: */*
> 
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: GET, POST, DELETE, PUT
< Access-Control-Allow-Headers: authorization, content-type
< Access-Control-Allow-Credentials: true
< content-length: 2
< content-type: text/plain
< 
* Connection #0 to host logstash-custerip left intact
okbash-4.2$ 
```

查看 hpa :
```shell script
kubectl -n logging get hpa
NAME           REFERENCE             TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
logstash-hpa   Deployment/logstash   <unknown>/80%   1         10        1          5m
```

演示就到这里，可以看到和真正的 kubernetes 使用并无两样。那么这里还有一个问题，启动的这个 pod 是如何运行的呢 ？

再次进到控制面的容器内看看 : 
```shell script
root@kind-control-plane:/# ps -ef 
UID          PID    PPID  C STIME TTY          TIME CMD
root           1       0  0 02:49 ?        00:00:00 /sbin/init
root         126       1  0 02:49 ?        00:00:00 /lib/systemd/systemd-journald
root         145       1  0 02:49 ?        00:01:12 /usr/local/bin/containerd
root         257       1  0 02:49 ?        00:00:03 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id c1a5e2c868b9a744f4f78a85a8d660950bb76103a38e7
root         271       1  0 02:49 ?        00:00:03 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 3549ecade28e2dccbad5ed15a4cd2b6e6a886cd3e10ab
root         297       1  0 02:49 ?        00:00:02 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 379ed27442f35696d488dd5a63cc61dc474bfa9bd08a9
root         335       1  0 02:49 ?        00:00:02 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id e4eae33bf489c617c7133ada7dbd92129f3f817cb74b7
root         343     271  0 02:49 ?        00:00:00 /pause
root         360     257  0 02:49 ?        00:00:00 /pause
root         365     297  0 02:49 ?        00:00:00 /pause
root         377     335  0 02:49 ?        00:00:00 /pause
root         443     335  0 02:49 ?        00:00:43 kube-scheduler --authentication-kubeconfig=/etc/kubernetes/scheduler.conf --authorization-kubeconfig=/etc/
root         468     297  3 02:49 ?        00:09:25 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --cli
root         496     271  0 02:49 ?        00:02:53 kube-controller-manager --allocate-node-cidrs=true --authentication-kubeconfig=/etc/kubernetes/controller-
root         540     257  1 02:49 ?        00:03:33 etcd --advertise-client-urls=https://172.18.0.2:2379 --cert-file=/etc/kubernetes/pki/etcd/server.crt --cli
root         580       1  1 02:49 ?        00:05:07 /usr/bin/kubelet --bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernete
root         673       1  0 02:50 ?        00:00:02 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id b0965a6f77f58c46cfe7b30dd84ddf4bc37516ba60e6e
root         695     673  0 02:50 ?        00:00:00 /pause
root         709       1  0 02:50 ?        00:00:03 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id aedf0f1fd02baf1cf2b253ad11e33e396d97cc7c53114
root         738     709  0 02:50 ?        00:00:00 /pause
root         789     673  0 02:50 ?        00:00:01 /usr/local/bin/kube-proxy --config=/var/lib/kube-proxy/config.conf --hostname-override=kind-control-plane
root         798     709  0 02:50 ?        00:00:02 /bin/kindnetd
root        1011       1  0 02:50 ?        00:00:02 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id aa554aa998c3091a70eacbc3e4a2f275a1e680a585d69
root        1024       1  0 02:50 ?        00:00:03 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 7373488f811fc5d638c2b3f5f79d953573e30a42ff52f
root        1048       1  0 02:50 ?        00:00:03 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 5ab6c3ef1715623e2c28fbfdecd5f4e6e2616fc20a387
root        1079    1011  0 02:50 ?        00:00:00 /pause
root        1088    1024  0 02:50 ?        00:00:00 /pause
root        1095    1048  0 02:50 ?        00:00:00 /pause
root        1152    1011  0 02:50 ?        00:00:35 /coredns -conf /etc/coredns/Corefile
root        1196    1024  0 02:50 ?        00:00:35 /coredns -conf /etc/coredns/Corefile
root        1205    1048  0 02:50 ?        00:00:13 local-path-provisioner --debug start --helper-image k8s.gcr.io/build-image/debian-base:v2.1.0 --config /et
root        1961       0  0 02:56 pts/1    00:00:00 bash
root       34093       1  0 07:27 ?        00:00:00 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id 438c08255ede5fb7fa93b37bcbe51807d2fa5e507122b
root       34115   34093  0 07:27 ?        00:00:00 /pause
1000       34151   34093  6 07:27 ?        00:01:05 /bin/java -Xms2g -Xmx2g -XX:+UseConcMarkSweepGC -XX:CMSInitiatingOccupancyFraction=75 -XX:+UseCMSInitiatin
root       36423       0  0 07:43 pts/2    00:00:00 bash
root       36540   36423  0 07:44 pts/2    00:00:00 ps -ef
```

可以看到 STIME 是 07:27 的就是刚刚启动 logstash 相关的进程，通过 containerd-shim-runc-v2 启动的 logstash 进程，/pause 为 pod的根容器。

## 环境清理
在本地体验完或者测试完成之后，为了节省资源，可以把刚刚启动的集群进行删除，下次需要时再创建即可 。
```shell script
kind delete cluster
Deleting cluster "kind" ...
[root@iZuf685opgs9oyozju9i2bZ k8s]# docker ps -a
CONTAINER ID        IMAGE                                    COMMAND                  CREATED             STATUS              PORTS                                      NAMES
4ec800c3ec10        russellgao/openresty:1.17.8.2-5-alpine   "/usr/local/openrest…"   8 weeks ago         Up 7 days           0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp   openresty-app-1
[root@iZuf685opgs9oyozju9i2bZ k8s]# kubectl -n logging get po 
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

通过上面的命令可以看出 : 

- 当执行 `kind delete cluster` 命令之后会把控制面的容器(kind-control-plane) 删除
- 当再次执行 kubectl 命令是已经无法找到对应的 api-server地址，可以查看 .kube/config 文件，发现已经删除了关于集群的配置信息。

## 总结
本篇介绍了 kind(kubernetes in docker) 的基本用法，可以在本地快速构建起kubernetes 环境，适合新人快速入门、调试k8s 相关组件，测试operator 等。


