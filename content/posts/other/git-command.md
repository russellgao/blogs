+++
title = "git 常用命令"
description = "git 常用命令"
date = "2020-12-14"
aliases = ["git 常用命令"]
author = "russellgao"
draft = false
tags = [
    "git",
    "cli"
]
+++

## 导读
> 这篇文章主要记录了 `git` 的一些常用命令，后续会持续补充更新。
>

## 常用命令
### 检出代码
```shell script
git clone url -b git_branch 
```

### 查看分支
```shell script
git branch -a 
```

### 创建分支
```shell script
git branch xxx
```

### 删除本地分支
```shell script
git branch -d xxxxx
```

### 检出分支
```shell script
git checkout git_branch 
```

### 拉取代码
```shell script
git pull 
```

### 把修改文件提交到缓冲区
```shell script
git add <filename>
```

### 本地提交
```shell script
git commit -m "代码提交信息"
```

### 推送代码
```shell script
git push origin local_branch:remote_branch          
例 : git push origin release/release:release/release
```

### 合并代码
```shell script
git merge origin/remote
```

### cherry pick 
```shell script
git cherry-pick commit_id
```

### 跟踪
```shell script
git branch --set-upstream-to=remote_branch local_branch     
例 git branch --set-upstream-to=origin/release/release release/release
```

### 丢弃本地修改
```shell script
git checkout -- file          
例 git checkout -- test.py
```

### 取消本地提交
```shell script
- git log 查找需要恢复的 commit_id
- git reset --hard commit_id
```

### 本地清除git上已经删除的分支
```shell script
git remote prune origin
```
