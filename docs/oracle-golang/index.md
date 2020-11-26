# 如何利用 golang 操纵 oracle


## 安装库
```shell script
pip3 install sqlalchemy
pip3 install cx_Oracle
```

## 安装客户端
oracle 客户端下载页面: https://www.oracle.com/database/technologies/instant-client/downloads.html

### mac
- https://www.oracle.com/database/technologies/instant-client/macos-intel-x86-downloads.html

在上面的页面下载之后执行:

```shell script
# 解压
cd ~
unzip instantclient-basic-macos.x64-19.3.0.0.0dbru.zip

# 创建link
mkdir ~/lib
ln -s ~/instantclient_19_3/libclntsh.dylib ~/lib/
```


### linux
- https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html

### windows
- https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html

## 使用
在上面装好库和oracle client 就可以用python 操作 oracle 了
