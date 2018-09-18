# -*- coding:utf8 -*-

from django.conf import settings
from Consumer_App.cs_common.models import TencentCloudCOSInfo, ImageCOSUrl, ImageSaveRecord
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from horizon import main
import os


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


class CosS3(metaclass=Singleton):
    def __init__(self):
        instance = TencentCloudCOSInfo.get_object()
        config = CosConfig(Secret_id=instance.secret_id,
                           Secret_key=instance.secret_key,
                           Region=instance.region,
                           Token='')
        self.bucket = instance.bucket
        # 默认下载链接有效期为2小时
        self.expires_in = 2 * 3600
        self.client = CosS3Client(config)

    def put_object(self, body, file_name):
        """
        简单上传文件（推荐上传不大于20M的小文件）
        :param body: 上传文件的内容，可以为文件流或字节流
        :param file_name: 上传文件的路径名，默认从 Bucket 开始
        :return: 
        """
        try:
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=body,
                Key=file_name,
            )
        except Exception as e:
            return e

        # 将该条记录保存到数据库中
        init_data = {'image_name': file_name}
        try:
            instance = ImageSaveRecord(**init_data)
            instance.save()
        except Exception as e:
            return e
        return response

    def get_presigned_download_url(self, file_name, expires_in=None):
        """
        获取预签名下载链接用于直接下载。
        :param file_name: 上传文件的路径名，默认从 Bucket 开始
        :param expires_in: 过期时间（单位：秒）
        :return: 有效的链接地址
        """
        if not file_name:
            return ''

        # 先查找file_name是否有有效的链接地址，如果不存在则从cos中生成
        access_url = ImageCOSUrl.get_image_url(file_name)
        if access_url:
            return access_url

        # file_name没有在有效期内的URL，去cos中生成
        # 先查找是否已经上传了该照片，如果没有上传，则先上传
        # 1. 查找是否上传了照片
        instance = ImageSaveRecord.get_object(image_name=file_name)
        if isinstance(instance, Exception):
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            fp = open(file_path, 'rb')
            self.put_object(fp, file_name)
            fp.close()

        # 2. 去cos中生成文件的有效链接
        if not expires_in:
            expires_in = self.expires_in
        try:
            access_url = self.client.get_presigned_download_url(
                Bucket=self.bucket,
                Key=file_name,
                Expired=expires_in
            )
        except Exception as e:
            return e

        # 保存在数据库中
        init_data = {'image_name': file_name,
                     'url': access_url,
                     'expires': main.make_time_delta(seconds=expires_in)}
        try:
            instance = ImageCOSUrl(**init_data)
            instance.save()
        except Exception as e:
            return e

        return access_url
