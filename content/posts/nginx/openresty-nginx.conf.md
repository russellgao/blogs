+++
title = "openresty 配置文件 （一）"
description = "openresty 配置文件 （一）"
date = "2020-11-22"
aliases = ["openresty 配置文件 （一）"]
author = "russellgao"
draft = false
tags = [
    "nginx",
    "openresty",
    "nginx.conf"
]

categories = [
    "openresty"
]

+++

## 导读
>openresty（nginx plus） 在日常工作中用的应该比较多，要想真正了解清楚其原理并不容易。我尝试着从配置的角度去分析 nginx 的基本原理。这篇主要介绍
>nginx.conf 这个配置文件，后续再介绍其他的配置文件。
>
>nginx.conf 中主要配置全局配置，配置好之后一般很少改动。

## nginx.conf 配置项说明
```shell script
#定义Nginx运行的用户和用户组
#user  nobody; 

#nginx进程数，建议设置为等于CPU总核心数。
worker_processes  1; 

#全局错误日志定义类型，[ debug | info | notice | warn | error | crit ]
#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#进程文件
#pid        logs/nginx.pid;

#指定进程可以打开的最大描述符
#工作模式与连接数上限
##这个指令是指当一个nginx进程打开的最多文件描述符数目，理论值应该是最多打开文件数（ulimit -n）与nginx进程数相除，但是nginx分配请求并不是那么均匀，所以最好与ulimit -n 的值保持一致。
#这是因为nginx调度时分配请求到进程并不是那么的均衡，所以假如填写10240，总并发量达到3-4万时就有进程可能超过10240了，这时会返回502错误。
worker_rlimit_nofile 65535;

events {
    #参考事件模型，use [ kqueue | rtsig | epoll | /dev/poll | select | poll ]; epoll模型
    #是Linux 2.6以上版本内核中的高性能网络I/O模型，linux建议epoll，如果跑在FreeBSD上面，就用kqueue模型。
    #补充说明：
    #与apache相类，nginx针对不同的操作系统，有不同的事件模型
    #A）标准事件模型
    #Select、poll属于标准事件模型，如果当前系统不存在更有效的方法，nginx会选择select或poll
    #B）高效事件模型
    #Kqueue：使用于FreeBSD 4.1+, OpenBSD 2.9+, NetBSD 2.0 和 MacOS X.使用双处理器的MacOS X系统使用kqueue可能会造成内核崩溃。
    #Epoll：使用于Linux内核2.6版本及以后的系统。
    #/dev/poll：使用于Solaris 7 11/99+，HP/UX 11.22+ (eventport)，IRIX 6.5.15+ 和 Tru64 UNIX 5.1A+。
    #Eventport：使用于Solaris 10。 为了防止出现内核崩溃的问题， 有必要安装安全补丁。
    use epoll
    
    
    #单个进程最大连接数（最大连接数=连接数+进程数）
    worker_connections  65535;
    
    #keepalive 超时时间
    keepalive_timeout 60;
    
    #客户端请求头部的缓冲区大小。这个可以根据你的系统分页大小来设置，一般一个请求头的大小不会超过1k，不过由于一般系统分页都要大于1k，所以这里设置为分页大小。
    #分页大小可以用命令getconf PAGESIZE 取得。
    #[root@web001 ~]# getconf PAGESIZE
    #但也有client_header_buffer_size超过4k的情况，但是client_header_buffer_size该值必须设置为“系统分页大小”的整倍数。
    client_header_buffer_size 4k;
    
    #这个将为打开文件指定缓存，默认是没有启用的，max指定缓存数量，建议和打开文件数一致，inactive是指经过多长时间文件没被请求后删除缓存。
    open_file_cache max=65535 inactive=60s;
    
    
    #这个是指多长时间检查一次缓存的有效信息。
    #语法:open_file_cache_valid time 默认值:open_file_cache_valid 60 使用字段:http, server, location 这个指令指定了何时需要检查open_file_cache中缓存项目的有效信息.
    open_file_cache_valid 80s;
    
    
    #open_file_cache指令中的inactive参数时间内文件的最少使用次数，如果超过这个数字，文件描述符一直是在缓存中打开的，如上例，如果有一个文件在inactive时间内一次没被使用，它将被移除。
    #语法:open_file_cache_min_uses number 默认值:open_file_cache_min_uses 1 使用字段:http, server, location  这个指令指定了在open_file_cache指令无效的参数中一定的时间范围内可以使用的最小文件数,如果使用更大的值,文件描述符在cache中总是打开状态.
    open_file_cache_min_uses 1;
    
    #语法:open_file_cache_errors on | off 默认值:open_file_cache_errors off 使用字段:http, server, location 这个指令指定是否在搜索一个文件是记录cache错误.
    open_file_cache_errors on;

    #默认是on。设置为on后，多个worker按串行方式来处理连接，也就是一个连接只有一个worker被唤醒，其他的处于休眠状态。
    #设置为off后，多个worker按并行方式来处理连接，也就是一个连接会唤醒所有的worker，知道连接分配完毕，没有取得连接的继续休眠。
    #当你的服务器连接数不多时，开启这个参数会让负载有一定程度的降低。但是当服务器的吞吐量很大时，为了效率，请关闭这个参数。
    multi_accept off;

}


#设定http服务器
http {
    #文件扩展名与文件类型映射表
    include       mime.types;
    #默认文件类型
    default_type  application/octet-stream;
    
    # 增加 header
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";

    #默认编码
    charset utf-8;

    #服务器名字的hash表大小
    #保存服务器名字的hash表是由指令server_names_hash_max_size 和server_names_hash_bucket_size所控制的。参数hash bucket size总是等于hash表的大小，并且是一路处理器缓存大小的倍数。在减少了在内存中的存取次数后，使在处理器中加速查找hash表键值成为可能。如果hash bucket size等于一路处理器缓存的大小，那么在查找键的时候，最坏的情况下在内存中查找的次数为2。第一次是确定存储单元的地址，第二次是在存储单元中查找键 值。因此，如果Nginx给出需要增大hash max size 或 hash bucket size的提示，那么首要的是增大前一个参数的大小.
    server_names_hash_bucket_size 128;
    
    #客户端请求头部的缓冲区大小。这个可以根据你的系统分页大小来设置，一般一个请求的头部大小不会超过1k，不过由于一般系统分页都要大于1k，所以这里设置为分页大小。分页大小可以用命令getconf PAGESIZE取得。
    client_header_buffer_size 32k;
    
    #客户请求头缓冲大小。nginx默认会用client_header_buffer_size这个buffer来读取header值，如果header过大，它会使用large_client_header_buffers来读取。
    large_client_header_buffers 4 64k;
    
    #设定通过nginx上传文件的大小
    client_max_body_size 8m;

    #开启目录列表访问，合适下载服务器，默认关闭。
    autoindex on;
    
    # 限流
    limit_req_zone $server_name zone=xiaozhi_log:50m rate=40r/s;
    limit_req_zone $server_name zone=tico_log:50m rate=40r/s;
    
    #开启限制IP连接数的时候需要使用
    #limit_zone crawler $binary_remote_addr 10m;

    # 日志格式定义，这里可以根据自己的日志规范进行自定义
    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';
    # 这里推荐一个日志格式
    log_format  custom     '[$time_local] $remote_addr $remote_user $request '
                            '$status $upstream_response_time $request_time $body_bytes_sent $http_referer '
                            '$http_user_agent $http_x_forwarded_for ' ;

    #access_log  logs/access.log  main;

    #开启高效文件传输模式，sendfile指令指定nginx是否调用sendfile函数来输出文件，对于普通应用设为 on，如果用来进行下载等应用磁盘IO重负载应用，可设置为off，以平衡磁盘与网络I/O处理速度，降低系统的负载。注意：如果图片显示不正常把这个改 成off。
    sendfile        on;

    #防止网络阻塞
    #tcp_nopush     on;

    #小的数据包不等待直接传输。默认为on，看上去是和tcp_nopush相反的功能，但是两边都为on时nginx也可以平衡这两个功能的使用
    tcp_nodelay on;

    #长连接超时时间，单位是秒
    #keepalive_timeout  0;
    keepalive_timeout  65;

    #FastCGI相关参数是为了改善网站的性能：减少资源占用，提高访问速度。
    fastcgi_connect_timeout 300;
    fastcgi_send_timeout 300;
    fastcgi_read_timeout 300;
    fastcgi_buffer_size 64k;
    fastcgi_buffers 4 64k;
    fastcgi_busy_buffers_size 128k;
    fastcgi_temp_file_write_size 128k;

    #gzip模块设置
    gzip on; #开启gzip压缩输出
    gzip_min_length 1k;    #最小压缩文件大小
    gzip_buffers 4 16k;    #压缩缓冲区
    gzip_http_version 1.0; #压缩版本（默认1.1，前端如果是squid2.5请使用1.0）
    gzip_comp_level 2;     #压缩等级
    gzip_types text/plain application/x-javascript text/css application/xml;    #压缩类型，默认就已经包含textml，所以下面就不用再写了，写上去也不会有问题，但是会有一个warn。
    gzip_vary on;
    
    # include 配置文件
    # 这里是全局配置，一般会把 server 和 upstram 配置单独放在 conf.d 目录下或者 其他的自定义的目录下，通过include 字段 include 进来。
    include /etc/nginx/conf.d/*.conf;
}
```

这里面的很多参数可能并不会用到，大部分使用默认的即可。

## nginx.conf 样例
```shell script
worker_processes  2;

events {
    worker_connections  65535;
}


http {
    include       mime.types;
    default_type  application/octet-stream;
    log_format  custom     '[$time_local] $remote_addr $remote_user $request '
                            '$status $upstream_response_time $request_time $body_bytes_sent $http_referer '
                            '$http_user_agent $http_x_forwarded_for ' ;

    client_body_temp_path /var/run/openresty/nginx-client-body;
    proxy_temp_path       /var/run/openresty/nginx-proxy;
    fastcgi_temp_path     /var/run/openresty/nginx-fastcgi;
    uwsgi_temp_path       /var/run/openresty/nginx-uwsgi;
    scgi_temp_path        /var/run/openresty/nginx-scgi;

    sendfile        on;
    keepalive_timeout  90;

    include /etc/nginx/conf.d/*.conf;
}
```

## 接下来
这是 openresty 配置文件系列篇，这篇介绍了 nginx.conf (全局配置) ，接下来还有 server 、 upstream、location 等介绍。
每天掌握一个知识点，积少成多，一周玩转 openresty 。

## 参考
- https://juejin.cn/post/6844903741678698510
