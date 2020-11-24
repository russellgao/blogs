# openresty 配置文件 （二）


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

## server 
server 模块是位于 http 模块下面，进行端口监听，并把请求转发到 upstream 或者直接响应，先看它的配置是什么样子。
```shell script
server {
    #配置监听端口
    listen       80;
    #配置访问域名，可以只有一个名称，也可以由多个名称并列，之间用空格隔开。每个名字就是一个域名，由两段或者三段组成，之间由点号“.”隔开
    # 第一个名称作为此虚拟主机的主要名称
    # server_name 更加详细的用法参考下面 server_name 一节
    server_name  russellgao.cn russellgao.com localhost 127.0.0.1;
    
    # log 在全局变量中已经配置，但是每个监听中也可以配置，这样做的好处，在分析日志时比较方便，通过日志就可以知道请求从哪个监听中进来的
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
        root   /usr/local/openresty/nginx/docs;
    }

}
```
一个 server 只能监听一个端口。

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

## upstream

## location

## 参考
- https://www.cnblogs.com/54chensongxia/p/12938929.html


