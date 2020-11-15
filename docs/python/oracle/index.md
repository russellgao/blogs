# 如何利用 python 操纵 oracle


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

简单用法参见 :
```python
from sqlalchemy import *

# 连接oracle
engine = create_engine('oracle://username:passwoed@xxxxx', encoding="utf8",echo=True)
connection = engine.connect()

# table, 会根据表名自动生成Table 对象
meta = MetaData()
t = Table("abcd",meta,autoload=True,autoload_with=engine)

# 获取列
columns = t.c
print(columns)

# 查询
# s = select([t])
# s = select([t]).where(t.c.name == "xxxx")
s = select([t]).where(t.c.code == "xxxx")


result = connection.execute(s)
for row in result :
    print(row[t.c.gid],row[t.c.code],row[t.c.name],row[t.c.note])

result.close()
print("end")

```



## 报错
如果报如下错误:
```
sqlalchemy.exc.DatabaseError: (cx_Oracle.DatabaseError) DPI-1047: Cannot locate a 64-bit Oracle Client library: "dlopen(libclntsh.dylib, 1): image not found". See https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html for help
(Background on this error at: http://sqlalche.me/e/13/4xp6)
```

说明oracle的 client 没有正确安装


如果报错如下:
```
sqlalchemy.exc.DatabaseError: (cx_Oracle.DatabaseError) ORA-01017: invalid username/password; logon denied
(Background on this error at: http://sqlalche.me/e/13/4xp6)
```
说明oracle 的用户密码不正确

##  参考
- https://docs.sqlalchemy.org/en/13/dialects/oracle.html
- https://www.cnblogs.com/iupoint/p/10932069.html


