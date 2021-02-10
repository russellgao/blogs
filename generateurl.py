# coding=utf-8
from __future__ import unicode_literals, print_function

import codecs
import fnmatch
import os
import requests

def writeLinesToFile(filename, lines, append=False, encoding=None):
    if (append == True):
        file_mode = "a"
    else:
        file_mode = "w"
    encoding = encoding or 'utf-8'
    with codecs.open(filename, file_mode, encoding=encoding) as fp:
        for line in lines:
            print(line, file=fp)


baseurl = "https://russellgao.cn"
filename = "content/posts"
lines = []

for root, dirnames, filenames in os.walk(filename):
    for filename in fnmatch.filter(filenames, "*"):
        if filename.startswith("_index"):
            continue
        if filename.endswith(".md") :
            filename = filename[:len(filename)-3]
        filename = "{}/{}".format(baseurl, filename)
        resp = requests.get(filename)
        if resp.status_code > 299 :
            continue
        lines.append(filename)

writeLinesToFile("urls.txt", lines)
