# -*- coding: utf-8 -*-
import os
import string
import random
import tempfile
import functools

import requests

import unittest
import pytest
from dotenv import load_dotenv
from fastapi import HTTPException
from freezegun import freeze_time

from qiniu import Auth, set_default, etag, PersistentFop, build_op, op_save, Zone, QiniuMacAuth
from qiniu import BucketManager, build_batch_copy, build_batch_rename, build_batch_move, build_batch_stat, \
    build_batch_delete, DomainManager
from qiniu import urlsafe_base64_encode, urlsafe_base64_decode, canonical_mime_header_key, entry, decode_entry

from qiniu.compat import is_py2, is_py3, b, json

import qiniu.config
import io
import urllib

from starlette.responses import StreamingResponse

from libs.sqlUtils import SqlUtils

StringIO = io.StringIO
urlopen = urllib.request.urlopen

load_dotenv()

access_key = os.getenv('QINIU_ACCESS_KEY')
secret_key = os.getenv('QINIU_SECRET_KEY')
bucket_name = os.getenv('QINIU_TEST_BUCKET')
source_path = os.getenv("QINIU_SOURCE_PATH")
cdn_url = os.getenv("QINIU_CDN_URL")
suffix = os.getenv("QINNIU_SUFFIX")

hostscache_dir = None


def rand_string(length):
    lib = string.ascii_uppercase
    return ''.join([random.choice(lib) for i in range(0, length)])


def create_temp_file(size):
    t = tempfile.mktemp()
    f = open(t, 'wb')
    f.seek(size - 1)
    f.write(b('0'))
    f.close()
    return t


def remove_temp_file(file):
    try:
        os.remove(file)
    except OSError:
        pass


class QnClient:
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)

    def get_paths(self, prefix="/", marker=None, limit=1000, delimiter="/"):
        """
        根据指定条件获取文件列表。

        :param prefix: 可选参数，指定文件名前缀，用于过滤文件。
        :param marker: 可选参数，指定从哪个文件名开始获取列表。
        :param limit: 可选参数，指定最多获取的文件数量，默认为10。
        :param delimiter: 可选参数，指定分隔符，用于对文件名进行分组。
        :return: 无直接返回值，但通过断言检查获取的文件列表不为空。
        """
        # 获取一个列表
        ret, eof, info = self.bucket.list(bucket_name, prefix, marker, limit, delimiter)

        # 确保返回的文件列表不为空
        assert len(ret.get('items')) is not None
        assert len(ret.get('commonPrefixes')) is not None

        sqUtils = SqlUtils()
        sqUtils.open_conn()

        params = []

        # 循环ret['commonPrefixes']插入数据
        for item in ret['commonPrefixes']:
            params.append((item, ''))

        sqUtils.insert_data("paths", params)

        sqUtils.close_conn()

        return ret['commonPrefixes']

    def get_file_list(self, prefix="/", marker=None, limit=1000, delimiter=None):
        """
        根据指定条件获取文件列表。

        :param prefix: 可选参数，指定文件名前缀，用于过滤文件。
        :param marker: 可选参数，指定从哪个文件名开始获取列表。
        :param limit: 可选参数，指定最多获取的文件数量，默认为10。
        :param delimiter: 可选参数，指定分隔符，用于对文件名进行分组。
        :return: 无直接返回值，但通过断言检查获取的文件列表不为空。
        """
        sqUtils = SqlUtils()
        sqUtils.open_conn()
        paths = sqUtils.query_data("paths")
        sqUtils.close_conn()
        if len(paths) == 0:
            paths = self.get_paths(prefix=source_path)

        # 随机从paths取一个元素
        prefixquery = random.choice(paths)
        if prefixquery != "" or prefixquery is not None:
            prefix = prefixquery

        ret, eof, info = self.bucket.list(bucket_name, prefix, marker, limit, delimiter)
        assert len(ret.get('items')) is not None

        # 文件列表
        filepaths = []
        # 遍历去掉不是图片的文件
        for item in ret['items']:
            if item['mimeType'].startswith('image/'):
                filepaths.append(item)

        sqUtils = SqlUtils()
        sqUtils.open_conn()
        params = []
        for item in filepaths:
            params.append((item['key'], item['hash'], item['fsize'], item['mimeType'], item['putTime'], item['type'],
                           item['status'], item['md5']))

        sqUtils.insert_data("files", params)
        sqUtils.close_conn()

        return filepaths

    def get_onefile_by_prefix(self):
        filepath = None
        sqUtils = SqlUtils()
        sqUtils.open_conn()
        files = sqUtils.query_data("files")
        sqUtils.close_conn()
        file_key = None
        if len(files) == 0:
            files = self.get_file_list(prefix=source_path)
            filepath = random.choice(files)
            file_key = filepath['key']
        if len(files) > 0:
            filepath = random.choice(files)
            file_key = filepath['keyname']

        cdn_image_url = cdn_url + "/" + file_key + suffix

        # 返回一个文件
        try:
            # 发起请求到CDN获取图片
            response = requests.get(cdn_image_url, stream=True)
            response.raise_for_status()  # 确保请求成功

            # 创建一个StreamingResponse对象来流式传输图片数据
            return StreamingResponse(response.raw, media_type=filepath['mimeType'])
        except requests.RequestException as e:
            # 如果请求失败，返回错误信息
            raise HTTPException(status_code=400, detail=f"Failed to retrieve image: {e}")
