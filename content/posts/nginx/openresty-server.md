+++
title = "openresty 配置文件 （二）"
description = "openresty 配置文件 （二）"
date = "2020-11-23"
aliases = ["openresty 配置文件 （二）"]
author = "russellgao"
draft = false
tags = [
    "nginx",
    "openresty",
    "server" ,
    "location"
]

categories = [
    "openresty"
]

+++

## 导读
> 这篇是继上一篇 [openresty 配置文件 （一）](../openresty-nginx.conf) 介绍了 openresty 全局配置之后，介绍
>openresty server 配置，server 的配置一般单独放在 `conf.d` 目录下。下面是我比较推荐的 `conf.d` 目录结构：
> ```
> [root@iZuf685opgs9oyozju9i2bZ conf.d]# tree 
>  .
>  ├── 443.conf
>  ├── 8080.conf
>  ├── 80.conf
>  └── upstream.conf
>  
>  0 directories, 4 files
> ```
> upstream 放在单独的 配置文件，当然如果比较多，可以按照 service/product 的维度再进行拆分。不同的监听放在单独的配置文件，相对来说比较好维护一点，也更容易自动化程序处理。
>
> 这篇文章比较长，可以通过目录直接跳转到自己感兴趣的部分。


## server 
server 模块是位于 http 模块下面，进行端口监听，并把请求转发到 upstream 或者直接响应，先看它的配置是什么样子。
```shell script
server {
    #配置监听端口
    # listen 详细配置参考 listen 一节
    listen       80;

    #配置访问域名，可以只有一个名称，也可以由多个名称并列，之间用空格隔开。每个名字就是一个域名，由两段或者三段组成，之间由点号“.”隔开
    # 第一个名称作为此虚拟主机的主要名称
    # server_name 更加详细的用法参考下面 server_name 一节
    server_name  russellgao.cn russellgao.com localhost 127.0.0.1;
    
    # log 在全局变量中已经配置，但是每个监听中也可以配置，这样做的好处，在分析日志时比较方便，通过日志就可以知道请求从哪个监听中进来的
    # 也可以放在具体的 location 中。
    access_log  /usr/local/openresty/nginx/logs/access.log  custom;
    error_log  /usr/local/openresty/nginx/logs/error.log;
    
    # ssl 配置
    ssl                  on;
    ssl_certificate      /usr/local/openresty/nginx/ssl/4753767.pem;
    ssl_certificate_key  /usr/local/openresty/nginx/ssl/4753767.key;
    ssl_session_timeout  5m;
    ssl_protocols  SSLv2 SSLv3 TLSv1 TLSv1.2 TLSv1.1;
    ssl_ciphers  HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers   on;

    # location 配置，location 介绍参考下面详细介绍
    location / {
        root   /usr/local/openresty/nginx/docs;
        index  index.html index.htm;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/local/openresty/nginx/html;
    }

    error_page   404  /404.html;
    location = /404.html {
        root   /usr/local/openresty/nginx/docs;
    }
}
```
一个 server 只能监听一个端口。
### listen 
listen 有三种配置语法。这个指令默认的配置值是：listen *:80 | *:8000；只能在server块种配置这个指令。
```
//第一种
listen address[:port] [default_server] [ssl] [http2 | spdy] [proxy_protocol] [setfib=number] [fastopen=number] [backlog=number] [rcvbuf=size] [sndbuf=size] [accept_filter=filter] [deferred] [bind] [ipv6only=on|off] [reuseport] [so_keepalive=on|off|[keepidle]:[keepintvl]:[keepcnt]];

//第二种
listen port [default_server] [ssl] [http2 | spdy] [proxy_protocol] [setfib=number] [fastopen=number] [backlog=number] [rcvbuf=size] [sndbuf=size] [accept_filter=filter] [deferred] [bind] [ipv6only=on|off] [reuseport] [so_keepalive=on|off|[keepidle]:[keepintvl]:[keepcnt]];

//第三种（可以不用重点关注）
listen unix:path [default_server] [ssl] [http2 | spdy] [proxy_protocol] [backlog=number] [rcvbuf=size] [sndbuf=size] [accept_filter=filter] [deferred] [bind] [so_keepalive=on|off|[keepidle]:[keepintvl]:[keepcnt]];
```
listen指令的配置非常灵活，可以单独制定ip，单独指定端口或者同时指定ip和端口。

关于上面的一些重要参数做如下说明：

- address：监听的IP地址（请求来源的IP地址），如果是IPv6的地址，需要使用中括号“[]”括起来，比如[fe80::1]等。
- port：端口号，如果只定义了IP地址没有定义端口号，就使用80端口。这边需要做个说明：要是你压根没配置listen指令，那么那么如果nginx以超级用户权限运行，则使用*:80，否则使用*:8000。多个虚拟主机可以同时监听同一个端口,但是server_name需要设置成不一样；
- default_server：假如通过Host没匹配到对应的虚拟主机，则通过这台虚拟主机处理。
- backlog=number：设置监听函数listen()最多允许多少网络连接同时处于挂起状态，在FreeBSD中默认为-1，其他平台默认为511。
- accept_filter=filter，设置监听端口对请求的过滤，被过滤的内容不能被接收和处理。本指令只在FreeBSD和NetBSD 5.0+平台下有效。filter可以设置为dataready或httpready，感兴趣的读者可以参阅Nginx的官方文档。
- bind：标识符，使用独立的bind()处理此address:port；一般情况下，对于端口相同而IP地址不同的多个连接，Nginx服务器将只使用一个监听命令，并使用bind()处理端口相同的所有连接。
- ssl：标识符，设置会话连接使用SSL模式进行，此标识符和Nginx服务器提供的HTTPS服务有关。


### server_name
用于配置虚拟主机的名称。语法是：
```
Syntax:	server_name name ...;
Default:	
server_name "";
Context:	server
```
对于name 来说，可以只有一个名称，也可以由多个名称并列，之间用空格隔开。每个名字就是一个域名，由两段或者三段组成，之间由点号“.”隔开。比如
```
server_name myserver.com www.myserver.com
```
在该例中，此虚拟主机的名称设置为myserver.com或www. myserver.com。Nginx服务器规定，第一个名称作为此虚拟主机的主要名称。

在name 中可以使用通配符“*”，但通配符只能用在由三段字符串组成的名称的首段或尾段，或者由两段字符串组成的名称的尾段，如：
```
server_name myserver.* *.myserver.com
```
另外name还支持正则表达式的形式

由于server_name指令支持使用通配符和正则表达式两种配置名称的方式，因此在包含有多个虚拟主机的配置文件中，可能会出现一个名称被多个虚拟主机的server_name匹配成功。那么，来自这个名称的请求到底要交给哪个虚拟主机处理呢？Nginx服务器做出如下规定：

a. 对于匹配方式不同的，按照以下的优先级选择虚拟主机，排在前面的优先处理请求。
1. 准确匹配server_name
2. 通配符在开始时匹配server_name成功
3. 通配符在结尾时匹配server_name成功
4. 正则表达式匹配server_name成功

b. 在以上四种匹配方式中，如果server_name被处于同一优先级的匹配方式多次匹配成功，则首次匹配成功的虚拟主机处理请求。

## location
### 基本语法
```shell script
location [=|~|~*|^~] /uri/ {
 ...
}
```

- = : 表示精确匹配后面的url
- ~ : 表示正则匹配，但是区分大小写
- ~* : 正则匹配，不区分大小写
- ^~ : 如果把这个前缀用于一个常规字符串,那么告诉nginx 如果路径匹配那么不测试正则表达式

#### 「=」 修饰符：要求路径完全匹配
```shell script
server {
    server_name russellgao.cn;
    location = /abcd {
    […]
    }
}
```

- https://russellgao.cn/abcd匹配
- https://russellgao.cn/ABCD可能会匹配 ，也可以不匹配，取决于操作系统的文件系统是否大小写敏感（case-sensitive）。
- https://russellgao.cn/abcd?param1&param2匹配，忽略 querystring
- https://russellgao.cn/abcd/不匹配，带有结尾的/
- https://russellgao.cn/abcde不匹配

#### 「~」修饰符：区分大小写的正则匹配
```shell script
server {
    server_name russellgao.cn;
    location ~ ^/abcd$ {
    […]
    }
}
```
`^/abcd$` 这个正则表达式表示字符串必须以`/`开始，以`d`结束，中间必须是`abc`，换言之只能匹配 `/abcd`

- https://russellgao.cn/abcd匹配（完全匹配）
- https://russellgao.cn/ABCD不匹配，大小写敏感
- https://russellgao.cn/abcd?param1&param2匹配
- https://russellgao.cn/abcd/不匹配，不能匹配正则表达式
- https://russellgao.cn/abcde不匹配，不能匹配正则表达式

#### 「~*」不区分大小写的正则匹配
```shell script
server {
    server_name russellgao.cn;
    location ~* ^/abcd$ {
    […]
    }
}
```
https://russellgao.cn/abcd匹配 (完全匹配)
https://russellgao.cn/ABCD匹配 (大小写不敏感)
https://russellgao.cn/abcd?param1&param2匹配
https://russellgao.cn/abcd/ 不匹配，不能匹配正则表达式
https://russellgao.cn/abcde 不匹配，不能匹配正则表达式

#### 「^~」修饰符
前缀匹配 如果该 location 是最佳的匹配，那么对于匹配这个 location 的字符串， 该修饰符不再进行正则表达式检测。注意，这不是一个正则表达式匹配，它的目的是优先于正则表达式的匹配。

### 查找的顺序及优先级
当有多条 location 规则时，nginx 有一套比较复杂的规则，优先级如下：

- 精确匹配 =
- 前缀匹配 ^~（立刻停止后续的正则搜索）
- 按文件中顺序的正则匹配 ~或~*
- 匹配不带任何修饰的前缀匹配。

这个规则大体的思路是:
```shell script
先精确匹配，没有则查找带有 ^~的前缀匹配，没有则进行正则匹配，最后才返回前缀匹配的结果（如果有的话）
```

### alias 与 root 区别
- root 实际访问文件路径会拼接URL中的路径
- alias 实际访问文件路径不会拼接URL中的路径

看一个例子 

```shell script
location ^~ /sta/ {  
   alias /usr/local/nginx/html/static/;  
}
```

>- 请求：https://russellgao.cn/sta/index.html
>- 实际访问：/usr/local/nginx/html/static/index.html 文件

```shell script
location ^~ /static/ {  
   root /usr/local/nginx/html/;  
}
```

>- 请求：https://russellgao.cn/static/index.html
>- 实际访问：/usr/local/nginx/html/static/index.html 文件

### rewrite
rewrite 模块主要用于重定向。

指令语法：`rewrite regex replacement[flag];` ，默认值为 `none` 。
看个简单例子 :

```shell script
location / {
        rewrite ^/(.*) https://russellgao.cn/$1 permanent;
    }
```

这是我 http 强转 https 的例子。

### 常用正则表达式
字符	 | 描述
 :-: | :-:
|\	|将后面接着的字符标记为一个特殊字符或者一个原义字符或一个向后引用
|^	|匹配输入字符串的起始位置
|$	|匹配输入字符串的结束位置
|*	|匹配前面的字符零次或者多次
|+	|匹配前面字符串一次或者多次
|?	|匹配前面字符串的零次或者一次
|.	|匹配除“\n”之外的所有单个字符
|(pattern)	|匹配括号内的pattern

### flag参数
标记符号 |	说明
 :-: | :-:
last	|本条规则匹配完成后继续向下匹配新的location URI规则
break	|本条规则匹配完成后终止，不在匹配任何规则
redirect	|返回302临时重定向
permanent	|返回301永久重定向

#### last 和 break关键字的区别
- last 匹配到了还会继续向下匹配
- break 匹配到了不会继续向下匹配，会终止掉

#### permanent 和 redirect关键字的区别
- last 和 break 当出现在location 之外时，两者的作用是一致的没有任何差异
- last 和 break 当出现在location 内部时：
    - rewrite … permanent 永久性重定向，请求日志中的状态码为301
    - rewrite … redirect 临时重定向，请求日志中的状态码为302

### proxy_pass
在nginx中配置proxy_pass代理转发时，如果在proxy_pass后面的url加/，表示绝对根路径；如果没有/，表示相对路径，把匹配的路径部分也给代理走。

假设我们访问地址为 :
```shell script
https://russellgao.cn/proxypass/index.html
```

1. 当配置为
```shell script
location /proxypass/ {
    proxy_pass https://russellgao.cn/;
}
```
代理到: `https://russellgao.cn/index.html`

2. 当配置为
```shell script
location /proxypass/ {
    proxy_pass https://russellgao.cn;
}
```
代理到: `https://russellgao.cn/proxypass/index.html`

**请注意：proxy_pass 最后没有 `/`**

3. 当配置为
```shell script
location /proxypass/ {
    proxy_pass https://russellgao.cn/test/;
}
```
代理到: `https://russellgao.cn/test/index.html`

4. 当配置为
```shell script
location /proxypass/ {
    proxy_pass https://russellgao.cn/test;
}
```
代理到: `https://russellgao.cn/testindex.html`

> nginx 的 ngx_http_proxy_module 和 ngx_stream_proxy_module 模块都有 proxy_pass ，下面看看两者之间的关系与区别。

#### ngx_http_proxy_module
语法: 
```shell script
proxy_pass URL
```
场景: 

- location
- if in location
- limit_except

> 设置后端代理服务器的协议(protocol)和地址(address),以及location中可以匹配的一个可选的URI。协议可以是"http"或"https"。地址可以是一个域名或ip地址和端口，或者一个 unix-domain socket 路径。 

例:

```shell script
location ~* (/api/v1/blog-server) {
    proxy_pass_header Server;
    proxy_pass http://blog_server;
}
```
#### ngx_stream_proxy_module
语法: 
```shell script
proxy_pass address;
```
场景: 

- server

> 设置后端代理服务器的地址。这个地址(address)可以是一个域名或ip地址和端口，或者一个 unix-domain socket路径。

例: 
```shell script
server {
    listen 127.0.0.1:12345;
    proxy_pass 127.0.0.1:8080;
}
```

>在两个模块中，两个proxy_pass都是用来做后端代理的指令。
 ngx_stream_proxy_module模块的proxy_pass指令只能在server段使用使用, 只需要提供域名或ip地址和端口。可以理解为端口转发，可以是tcp端口，也可以是udp端口。
 ngx_http_proxy_module模块的proxy_pass指令需要在location段，location中的if段，limit_except段中使用，处理需要提供域名或ip地址和端口外，还需要提供协议，如"http"或"https"，还有一个可选的uri可以配置。


### 常见 location 配置样例
#### 静态网站
```shell script
server {
    listen       80;
    server_name  russellgao.cn;
    access_log  /usr/local/openresty/nginx/logs/access.log  custom;
    error_log  /usr/local/openresty/nginx/logs/error.log;
    
    location / {
        rewrite ^/(.*) https://russellgao.cn/$1 permanent;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/local/openresty/nginx/html;
    }

    error_page   404  /404.html;
    location = /404.html {
        root   /usr/local/openresty/nginx/blog;
    }
}
```

#### 反向代理
```shell script
location ~* (/api/v1/blog-server) {
    access_log  /var/nginx/logs/blog_access.log  custom;
    error_log   /var/nginx/logs/blog_error.log  error;
    proxy_pass_header Server;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Scheme $scheme;
    # rewrite 只是举个例子，根据实际情况配置
#    rewrite /api/v1/blog-server/(.*)$ /api/$1 break;
    proxy_pass http://blog_server;
}
```
- 可以在 location 级别设置日志格式以及目录，方便精细化管理
- 通过proxy_pass 跳转到 `upstream`

## upstream
upstream 是后端服务器组，也称为虚拟服务器组，作用是负载均衡。配置样例参考

```shell script
upstream blog_server {
    #upstream的负载均衡，weight是权重，可以根据机器配置定义权重。weigth参数表示权值，权值越高被分配到的几率越大。
    server 172.19.208.76:80 weight=10;
    server 172.19.208.77:80 weight=50;
    server 172.19.208.78:80 weight=40;
}
```
nginx的upstream目前支持 5 种方式的分配:

- 轮询（默认）：每个请求按时间顺序逐一分配到不同的后端服务。如:
    ```shell script
  upstream server {
        server 172.19.208.76:80;
        server 172.19.208.77:80;
        server 172.19.208.78:80;
  }
    ```
- 权重 ：指定轮询几率，weight和访问比率成正比，用于后端服务器性能不均的情况。
    ```shell script
  upstream server {
        server 172.19.208.76:80 weight=10;
        server 172.19.208.77:80 weight=50;
        server 172.19.208.78:80 weight=40;
  }
    ```
- ip_hash：每个请求按访问ip的hash结果分配，这样每个访客固定访问一个后端服务器，可以解决session的问题。
    ```shell script
    upstream server {
        ip_hash;
        server 172.19.208.76:80;
        server 172.19.208.77:80;
        server 172.19.208.78:80;
    }
    ```
- fair：按后端服务器的响应时间来分配请求，响应时间短的优先分配。
    ```shell script
    upstream server {
        fair;
        server 172.19.208.76:80;
        server 172.19.208.77:80;
        server 172.19.208.78:80;
    }
    ```
- url_hash：按访问url的hash结果来分配请求，使每个url定向到同一个后端服务器，后端服务器为缓存时比较有效。在upstream中加入hash语句，server语句中不能写入weight等其他的参数，hash_method是使用的hash算法。如:
    ```shell script
    upstream server {
        hash $request_uri;
        hash_method crc32;
        server 172.19.208.76:80;
        server 172.19.208.77:80;
        server 172.19.208.78:80;
    }
    ```

在 upstream 中可以给 server 设置状态，如:
```shell script
upstream server {
    server 172.19.208.76:80 down;
    server 172.19.208.77:80 weight=10;
    server 172.19.208.78:80 backup;
}
```

支持的状态有: 

1. down表示单前的server暂时不参与负载
2. weight为weight越大，负载的权重就越大。
3. max_fails：允许请求失败的次数默认为1.当超过最大次数时，返回proxy_next_upstream模块定义的错误
4. fail_timeout:max_fails次失败后，暂停的时间。
5. backup： 其它所有的非backup机器down或者忙的时候，请求backup机器。所以这台机器压力会最轻。

## 参考
- https://www.cnblogs.com/54chensongxia/p/12938929.html
- https://juejin.cn/post/6844903849166110733
