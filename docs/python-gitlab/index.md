# python-gitlab 库详解


## 导读
> 本文主要讲解如何用 `python-gitlab` 操作 gitlab。官方文档参考: [https://python-gitlab.readthedocs.io/en/stable/index.html](https://python-gitlab.readthedocs.io/en/stable/index.html) 。
>
> 本文实验的 python 环境: 2.7.15

## 安装
首先需要安装 `python-gitlab` 库

### pip 安装
```shell script
sudo pip install --upgrade python-gitlab
```

### 源码安装
```shell script
git clone https://github.com/python-gitlab/python-gitlab
cd python-gitlab
sudo python setup.py install
```

## 用法
### CLI 用法
首先需要对环境进行配置才能使用 cli ，需要提供一个配置文件，指明 gitlab server 信息以及连接参数，配置文件格式为 `INI` ,样例如下:
```
[global]
default = somewhere
ssl_verify = true
timeout = 5

[somewhere]
url = https://some.whe.re
private_token = vTbFeqJYCY3sibBP7BZM
api_version = 4

[elsewhere]
url = http://else.whe.re:8080
private_token = CkqsjqcQSFH5FQKDccu4
timeout = 1
```

- 其中 `global` 部分是必须提供的，主要是连接 gitlab 的参数
- 其他部分是可选，当没有配置时默认用的是 default
- 使用过程中可以通过 `-g` 指定具体使用的是那一节，如 `gitlab -g somewhere project list `

本文使用的配置文件如下 :
```
[global]
ssl_verify = true
timeout = 5

[gitlab]
url = https://gitlab-russellgo.cn
private_token = xxxxxx
api_version = 4
```

配置文件可以通过以下几种方法生效 :

- 通过环境变量配置 `PYTHON_GITLAB_CFG`
- 放在系统配置下 `/etc/python-gitlab.cfg`
- 放在当前用户 home 目录下 `~/.python-gitlab.cfg`
- 通过命令行指定 `-c` 或者 `--config-file`

本文的配置文件放在了 home 下。

当配置好了环境就可以愉快的使用了

- 列出所有的 project （分页返回）
    ```shell script
    # 上面定义了一个 gitlab 的组，所以执行时可以通过 -g 指定
    gitlab -g gitlab project list
    ```
- 列出所有的 project
    ```shell script
    gitlab -g gitlab project list --all
    ``` 

试到这里有个疑问，怎么知道 `gitlab` 目前支持哪些命令呢 
```shell script
gitlab -g gitlab 
# 以下是输出
usage: gitlab [-h] [--version] [-v] [-d] [-c CONFIG_FILE] [-g GITLAB]
              [-o {json,legacy,yaml}] [-f FIELDS]
              {application-settings,audit-event,broadcast-message,current-user,current-user-email,current-user-gp-gkey,current-user-key,current-user-status,deploy-key,dockerfile,event,feature,geo-node,gitignore,gitlabciyml,group,group-access-request,group-badge,group-board,group-board-list,group-cluster,group-custom-attribute,group-epic,group-epic-issue,group-epic-resource-label-event,group-issue,group-label,group-member,group-merge-request,group-milestone,group-notification-settings,group-project,group-subgroup,group-variable,hook,issue,l-da-pgroup,license,merge-request,namespace,notification-settings,pages-domain,project,project-access-request,project-additional-statistics,project-approval,project-approval-rule,project-badge,project-board,project-board-list,project-branch,project-cluster,project-commit,project-commit-comment,project-commit-discussion,project-commit-discussion-note,project-commit-status,project-custom-attribute,project-deployment,project-environment,project-event,project-export,project-file,project-fork,project-hook,project-import,project-issue,project-issue-award-emoji,project-issue-discussion,project-issue-discussion-note,project-issue-link,project-issue-note,project-issue-note-award-emoji,project-issue-resource-label-event,project-issues-statistics,project-job,project-key,project-label,project-member,project-merge-request,project-merge-request-approval,project-merge-request-award-emoji,project-merge-request-diff,project-merge-request-discussion,project-merge-request-discussion-note,project-merge-request-note,project-merge-request-note-award-emoji,project-merge-request-resource-label-event,project-milestone,project-note,project-notification-settings,project-pages-domain,project-pipeline,project-pipeline-job,project-pipeline-schedule,project-pipeline-schedule-variable,project-pipeline-variable,project-protected-branch,project-protected-tag,project-push-rules,project-registry-repository,project-registry-tag,project-release,project-runner,project-service,project-snippet,project-snippet-award-emoji,project-snippet-discussion,project-snippet-discussion-note,project-snippet-note,project-snippet-note-award-emoji,project-tag,project-trigger,project-user,project-variable,project-wiki,runner,runner-job,snippet,todo,user,user-activities,user-custom-attribute,user-email,user-event,user-gp-gkey,user-impersonation-token,user-key,user-project,user-status}
```

这样可以列出当前 gitlab 支持的资源，知道了支持的资源，那有怎么知道某种资源支持哪些操作的，以 project 为例，
````shell script
gitlab -g gitlab project 
# 以下是输出
usage: gitlab project [-h]
                      {list,get,create,update,delete,repository-blob,repository-contributors,delete-merged-branches,share,archive,repository-compare,create-fork-relation,languages,mirror-pull,unarchive,star,search,artifact,trigger-pipeline,repository-archive,delete-fork-relation,repository-raw-blob,repository-tree,unstar,housekeeping,unshare,upload,snapshot,update-submodule,transfer-project}
                      ...
gitlab project: error: too few arguments
````

这样就可以知道 `gitlab` 支持对何种资源做哪些操作，再通过 `--help` 就可以知道具体的参数，如 
```shell script
gitlab -g gitlab project list  --help 
# 以下是输出
usage: gitlab project list [-h] [--sudo SUDO] [--search SEARCH]
                           [--owned OWNED] [--starred STARRED]
                           [--archived ARCHIVED] [--visibility VISIBILITY]
                           [--order-by ORDER_BY] [--sort SORT]
                           [--simple SIMPLE] [--membership MEMBERSHIP]
                           [--statistics STATISTICS]
                           [--with-issues-enabled WITH_ISSUES_ENABLED]
                           [--with-merge-requests-enabled WITH_MERGE_REQUESTS_ENABLED]
                           [--with-custom-attributes WITH_CUSTOM_ATTRIBUTES]
                           [--page PAGE] [--per-page PER_PAGE] [--all]

optional arguments:
  -h, --help            show this help message and exit
  --sudo SUDO
  --search SEARCH
  --owned OWNED
  --starred STARRED
  --archived ARCHIVED
  --visibility VISIBILITY
  --order-by ORDER_BY
  --sort SORT
  --simple SIMPLE
  --membership MEMBERSHIP
  --statistics STATISTICS
  --with-issues-enabled WITH_ISSUES_ENABLED
  --with-merge-requests-enabled WITH_MERGE_REQUESTS_ENABLED
  --with-custom-attributes WITH_CUSTOM_ATTRIBUTES
  --page PAGE
  --per-page PER_PAGE
  --all

```

这样就可以很方便的对 `gitlab` 进行操作了。

### 编程用法
除了通过命令行操作 gitlab 之外，还可以用编程的方式进行集成，一个常见的场景，要从 gitlab 中下载某个文件


#### 基本用法 
```python
#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import gitlab

# 实例化一个 gitlab 对象
url = "https://gitlab.russellgao.cn"
private_token = "xxxxxxxx"
gl = gitlab.Gitlab('https://gitlab.russellgao.cn', private_token=private_token)

# 列出所有的项目
projects = gl.projects.list()
for project in projects:
    print(project)

# 获取 group id 是 2 的 list
group = gl.groups.get(2)
for project in group.projects.list():
    print(project)

# 创建一个用户
user_data = {'email': 'jen@foo.com', 'username': 'jen', 'name': 'Jen'}
user = gl.users.create(user_data)
print(user)

# 列出 create 和 update 时需要的参数
# get_create_attrs() 创建时需要的参数
# get_update_attrs() 更新时需要的参数

print(gl.projects.get_create_attrs())
(('name',), ('path', 'namespace_id', ...))

# 返回的是两个元组， 第一个 必选的参数，第二个是可选的参数

# 获取 对象的属性 ，如 project
project = gl.projects.get(1)
print(project.attributes)

# 有些对象提供了 gitlab 相关的资源属性
project = gl.projects.get(1)
issues = project.issues.list()

# python-gitlab 允许向 gitlab 发送任何数据，当发送非法数据或者缺少相关参数时会抛出异常

gl.projects.list(sort='invalid value')
# ...
# GitlabListError: 400: sort does not have a valid value

# 通过 query_parameters 进行传参 当参数和python 关键字冲突时
gl.user_activities.list(from='2019-01-01')  ## invalid
gl.user_activities.list(query_parameters={'from': '2019-01-01'})  # OK
```

#### 函数封装例子
通过 gitlab raw url 进行下载文件

```python
def download_gitlab_file(url, filename, private_token) :
    """
    从 gitlab 上下载文件

    :param url: gitlab raw url
    :param filename: 保存到本地的文件名称
    :param private_token:
    :return:
    """
    import gitlab
    import codecs

    def writeLinesToFile(filename, lines, append=False, encoding=None):
        if (append == True):
            file_mode = "a"
        else:
            file_mode = "w"
        encoding = encoding or 'utf-8'
        with codecs.open(filename, file_mode, encoding=encoding) as fp:
            for line in lines:
                print(unicode(line), file=fp)

    url_patterns = url.split("/")
    if len(url_patterns) < 8 :
        raise ValueError("url: `{}` 参数不合法，以 / 分隔之后长度必须大于8".format(url))
    baseurl = "{}//{}".format(url_patterns[0], url_patterns[2])
    namespace = url_patterns[3]
    project_name = url_patterns[4]
    branch = url_patterns[6]
    url_filename = "/".join(url_patterns[7:])
    if url_patterns[5] == "-" :
        branch = url_patterns[7]
        url_filename = "/".join(url_patterns[8:])

    gl = gitlab.Gitlab(str(baseurl), private_token)
    projects = gl.projects.list(search=project_name)
    projects = filter(lambda x : x.namespace.get("full_path") == namespace, projects )
    if len(projects) == 0 :
        raise ValueError("根据url 没有找到相应的 project ,请检查当前用户是否有权限或者 url 是否正确 ")
    project = projects[0]
    raw_content = project.files.raw(file_path=url_filename, ref=branch)
    writeLinesToFile(filename, [raw_content])
    return raw_content

```

## 源码解析
源码地址: [https://github.com/python-gitlab/python-gitlab/](https://github.com/python-gitlab/python-gitlab/)

从 [setup.py#L31:5](https://sourcegraph.com/github.com/python-gitlab/python-gitlab/-/blob/setup.py#L31:5) 中可以看出

```python
from setuptools import setup
from setuptools import find_packages
...
setup(
    name="python-gitlab",
    ...
    entry_points={"console_scripts": ["gitlab = gitlab.cli:main"]},
    ....
)
```

python-gitlab 采用 setuptools 进行打包，打成的包有两个作用:

- 当作 python 库使用 （默认） 
- `entry_points={"console_scripts": ["gitlab = gitlab.cli:main"]}` 说明可以当作 cli 使用，指令是 `gitlab` ，真正调用的是 `gitlab.cli:main` 函数

在看一下 `cli.py` 这个入口文件，从入口文件可以看到 [cli.py#L182:14](https://sourcegraph.com/github.com/python-gitlab/python-gitlab/-/blob/gitlab/cli.py#L182:14)

```python
def main():
    import gitlab.v4.cli
...
    # 可以跳转到这个函数中查看
    parser = _get_base_parser(add_help=False)
...

def _get_base_parser(add_help: bool = True) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=add_help, description="GitLab API Command Line Interface"
    )
    parser.add_argument("--version", help="Display the version.", action="store_true")
    parser.add_argument(
        "-v",
        "--verbose",
        "--fancy",
        help="Verbose mode (legacy format only)",
        action="store_true",
    )
...
```

这里可以 cli 解析库用的是 `argparse` 做命令行参数的解析 。

通过 `GitlabCLI` class [cli.py#L29:7](https://sourcegraph.com/github.com/python-gitlab/python-gitlab/-/blob/gitlab/v4/cli.py#L29:7) 可以看出

```python
class GitlabCLI(object):
    def __init__(self, gl, what, action, args):
        self.cls_name = cli.what_to_cls(what)
        self.cls = gitlab.v4.objects.__dict__[self.cls_name]
        self.what = what.replace("-", "_")
        self.action = action.lower()
        self.gl = gl
        self.args = args
        self.mgr_cls = getattr(gitlab.v4.objects, self.cls.__name__ + "Manager")
        # We could do something smart, like splitting the manager name to find
        # parents, build the chain of managers to get to the final object.
        # Instead we do something ugly and efficient: interpolate variables in
        # the class _path attribute, and replace the value with the result.
        self.mgr_cls._path = self.mgr_cls._path % self.args
        self.mgr = self.mgr_cls(gl)

        if self.mgr_cls._types:
            for attr_name, type_cls in self.mgr_cls._types.items():
                if attr_name in self.args.keys():
                    obj = type_cls()
                    obj.set_from_cli(self.args[attr_name])
                    self.args[attr_name] = obj.get()
```

cli 基本格式为 `gitlab what action args` ,即上面 `cli` 章节提到的 `gitlab 支持的资源 做什么操作 这个操作对应的参数`  

通过走读 `client.py` [client.py#L446:9](https://sourcegraph.com/github.com/python-gitlab/python-gitlab/-/blob/gitlab/client.py#L446:9) 
这个文件可以看到
```python
def http_request(
        self,
        verb: str,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
        post_data: Optional[Dict[str, Any]] = None,
        streamed: bool = False,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Make an HTTP request to the Gitlab server.

        Args:
            verb (str): The HTTP method to call ('get', 'post', 'put',
                        'delete')
            path (str): Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data (dict): Data to send as query parameters
            post_data (dict): Data to send in the body (will be converted to
                              json)
            streamed (bool): Whether the data should be streamed
            files (dict): The files to send to the server
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object.

        Raises:
            GitlabHttpError: When the return code is not 2xx
        """
        query_data = query_data or {}
        url = self._build_url(path)

        params: Dict[str, Any] = {}
        utils.copy_dict(params, query_data)

        # Deal with kwargs: by default a user uses kwargs to send data to the
        # gitlab server, but this generates problems (python keyword conflicts
        # and python-gitlab/gitlab conflicts).
        # So we provide a `query_parameters` key: if it's there we use its dict
        # value as arguments for the gitlab server, and ignore the other
        # arguments, except pagination ones (per_page and page)
        if "query_parameters" in kwargs:
            utils.copy_dict(params, kwargs["query_parameters"])
            for arg in ("per_page", "page"):
                if arg in kwargs:
                    params[arg] = kwargs[arg]
        else:
            utils.copy_dict(params, kwargs)

        opts = self._get_session_opts(content_type="application/json")

        verify = opts.pop("verify")
        timeout = opts.pop("timeout")
        # If timeout was passed into kwargs, allow it to override the default
        timeout = kwargs.get("timeout", timeout)

        # We need to deal with json vs. data when uploading files
        if files:
            json = None
            if post_data is None:
                post_data = {}
            post_data["file"] = files.get("file")
            post_data["avatar"] = files.get("avatar")
            data = MultipartEncoder(post_data)
            opts["headers"]["Content-type"] = data.content_type
        else:
            json = post_data
            data = None

        # Requests assumes that `.` should not be encoded as %2E and will make
        # changes to urls using this encoding. Using a prepped request we can
        # get the desired behavior.
        # The Requests behavior is right but it seems that web servers don't
        # always agree with this decision (this is the case with a default
        # gitlab installation)
        req = requests.Request(verb, url, json=json, data=data, params=params, **opts)
        prepped = self.session.prepare_request(req)
        prepped.url = utils.sanitized_url(prepped.url)
        settings = self.session.merge_environment_settings(
            prepped.url, {}, streamed, verify, None
        )

        # obey the rate limit by default
        obey_rate_limit = kwargs.get("obey_rate_limit", True)
        # do not retry transient errors by default
        retry_transient_errors = kwargs.get("retry_transient_errors", False)

        # set max_retries to 10 by default, disable by setting it to -1
        max_retries = kwargs.get("max_retries", 10)
        cur_retries = 0
...
```

通过对 requests 和 gitlab server 进行通信和数据交换 。

总体而言 ， `python-gitlab` 提供了 [Gitlab](https://sourcegraph.com/github.com/python-gitlab/python-gitlab/-/blob/gitlab/client.py#L58:9) 
和 [GitlabCLI](https://sourcegraph.com/github.com/python-gitlab/python-gitlab/-/blob/gitlab/v4/cli.py#L29:7) 两个对象给到客户端使用，提供了一系列的封装，通过 `requests` 库和 gitlab server 进行通信 。

## 参考
- https://python-gitlab.readthedocs.io/en/stable/index.html
- https://github.com/python-gitlab/python-gitlab/

