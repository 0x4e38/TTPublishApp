# -*- coding:utf8 -*-
from oauthlib.common import generate_token
from django.core.files.uploadedfile import (InMemoryUploadedFile,
                                            TemporaryUploadedFile)
from django.conf import settings
from django.utils.timezone import now
from lxml import etree
import datetime
import qrcode
import json
import os
import uuid
from hashlib import md5
from barcode import generate
from barcode.writer import ImageWriter
import base64
import random
import time
import uuid
import hmac
import copy
import math
import io
import gzip
import tarfile
import rarfile
import zipfile
import xlrd
import csv

# 图片处理类
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import StringIO, BytesIO

from horizon import http_requests


def minutes_5_plus():
    return now() + datetime.timedelta(minutes=5)


def minutes_15_plus():
    return now() + datetime.timedelta(minutes=15)


def minutes_30_plus():
    return now() + datetime.timedelta(minutes=30)


def hours_2_plus():
    return now() + datetime.timedelta(hours=2)


def days_7_plus():
    return now() + datetime.timedelta(days=7)


def make_time_delta(days=0, minutes=0, seconds=0):
    """
    设置时间增量
    """
    return now() + datetime.timedelta(days=days,
                                      minutes=minutes,
                                      seconds=seconds)


def make_time_delta_for_custom(date_time, days=0, hours=0, minutes=0, seconds=0):
    """
    设置时间增量
    """
    return date_time + datetime.timedelta(days=days,
                                          hours=hours,
                                          minutes=minutes,
                                          seconds=seconds)


def make_millisecond_time_stamp():
    time_stamp = '%s' % int(time.time() * 1000)
    return time_stamp


def make_perfect_time_delta(days=0, hours=0, minutes=0, seconds=0):
    """
    设置时间增量
    """
    now_date = datetime.datetime.strftime(now().date(), '%Y-%m-%d %H:%M:%S')
    now_datetime = datetime.datetime.strptime(now_date, '%Y-%m-%d %H:%M:%S')
    return now_datetime + datetime.timedelta(days=days,
                                             hours=hours,
                                             minutes=minutes,
                                             seconds=seconds)


def get_random_millisecond(min_value=15*1000, max_value=60*1000):
    """
    获取随机毫秒数
    :param min_value: 最小毫秒数
    :param max_value: 最大毫秒数
    :return: 
    """
    return random.randint(min_value, max_value)


class DatetimeEncode(json.JSONEncoder):
    """
    让json模块可以序列化datetime类型的字段
    """
    def default(self, o):
        from django.db.models.fields.files import ImageFieldFile

        if isinstance(o, datetime.datetime):
            return str(o)
        elif isinstance(o, ImageFieldFile):
            return str(o)
        else:
            return json.JSONEncoder.default(self, o)


def timezoneStringTostring(timezone_string):
    """
    rest framework用JSONRender方法格式化datetime.datetime格式的数据时，
    生成数据样式为：2017-05-19T09:40:37.227692Z 或 2017-05-19T09:40:37Z
    此方法将数据样式改为："2017-05-19 09:40:37"，
    返回类型：string
    """
    if not isinstance(timezone_string, (str, bytes)):
        return ""
    if not timezone_string:
        return ""
    timezone_string = timezone_string.split('.')[0]
    timezone_string = timezone_string.split('Z')[0]
    try:
        timezone = datetime.datetime.strptime(timezone_string, '%Y-%m-%dT%H:%M:%S')
    except:
        return ""
    return str(timezone)


QRCODE_PICTURE_PATH = settings.PICTURE_DIRS['consumer']['qrcode']


def make_qrcode(source_data, save_path=QRCODE_PICTURE_PATH, version=5):
    """
    生成二维码图片
    """
    qr = qrcode.QRCode(version=version,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4)
    qr.add_data(source_data)
    qr.make(fit=True)
    fname = "%s.png" % make_random_char_and_number_of_string(20)
    fname_path = os.path.join(save_path, fname)

    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    image = qr.make_image()
    image.save(fname_path)
    return fname_path


def make_barcode(save_path=QRCODE_PICTURE_PATH, barcode_length=8):
    """
    生成条形码
    返回：条形码数字及条形码文件名
    """
    source_data = make_random_number_of_string(barcode_length)
    generate_dict = {8: {'name': 'EAN8',
                         'width': 0.96},
                     13: {'name': 'EAN13',
                          'width': 0.66}
                     }
    fname = '%s.png' % make_random_char_and_number_of_string(20)
    fname_path = os.path.join(save_path, fname)
    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    fp = open(fname_path, 'wb')
    writer = ImageWriter()
    generate_name = generate_dict[barcode_length]['name']
    width = generate_dict[barcode_length]['width']
    generate(generate_name, source_data, writer=writer, output=fp,
             writer_options={'module_width': width,
                             'module_height': 30})
    fp.close()

    return writer.text, fname_path


def make_static_url_by_file_path(file_path):
    path_list = file_path.split('static/', 1)
    return os.path.join(settings.WEB_URL_FIX, 'static', path_list[1])


def anaysize_xml_to_dict(source):
    """
    解析xml字符串
    """
    root = etree.fromstring(source)
    result = {article.tag: article.text for article in root}
    return result


def make_dict_to_xml(source_dict, use_cdata=True):
    """
    生成xml字符串
    """
    if not isinstance(source_dict, dict):
        raise ValueError('Parameter must be dict.')

    xml = etree.Element('xml')
    for _key, _value in source_dict.items():
        _key_xml = etree.SubElement(xml, _key)
        if _key == 'detail':
            _key_xml.text = etree.CDATA(_value)
        else:
            if not isinstance(_value, (bytes, str)):
                _value = str(_value)
            if use_cdata:
                _key_xml.text = etree.CDATA(_value)
            else:
                _key_xml.text = _value

    xml_string = etree.tostring(xml,
                                pretty_print=True,
                                encoding="UTF-8",
                                method="xml",
                                xml_declaration=True,
                                standalone=None)
    return xml_string.split('\n', 1)[1]


def make_dict_to_verify_string(params_dict):
    """
    将参数字典转换成待签名的字符串
    （对字典的KEY值进行字符串排序，然后将排序后的字符串连接起来）
    """
    params_list = []
    for key, value in params_dict.items():
        if not value or key == 'sign':
            continue
        params_list.append({'key': key, 'value': value})
    params_list.sort(key=lambda x: x['key'])
    params_strs = []
    for item in params_list:
        params_strs.append('%s=%s' % (item['key'], (item['value']).encode('utf8')))
    return '&'.join(params_strs)


def make_sign_with_hmacmd5(verify_string, secret_key):
    """
    通用的生成签名的函数（hMac MD5加密哈希算法）
    :param verify_string: 待签名的字符串
    :param secret_key: 随机字符串
    :return: 大写的md5
    """
    if isinstance(verify_string, dict):
        verify_string = make_dict_to_verify_string(verify_string)

    hmac_string = hmac.new(secret_key, verify_string).hexdigest()
    return hmac_string.upper()


def make_random_number_of_string(str_length=6):
    """
    生成数字型的随机字符串（最大长度：128位）
    """
    if str_length > 128:
        str_length = 128
    random_str = _random_str = str(random.random()).split('.')[1]
    for i in range(str_length // len(_random_str)):
        random_str += str(random.random()).split('.')[1]
    index_start = random.randint(0, len(random_str) - str_length)
    return random_str[index_start: index_start + str_length]


def make_random_char_and_number_of_string(str_length=32):
    """
    生成英文字符和数字混合型的字符串（最大长度：128位）
    """
    if str_length > 128:
        str_length = 128
    return generate_token(length=str_length)


def get_time_stamp():
    stamp = str(time.time()).split('.')[0]
    return stamp


MEDIA_IMAGE_PATH = os.path.join(settings.MEDIA_ROOT, settings.PICTURE_DIRS['business']['clothes'])


class BaseImage(object):
    """
    图片处理类：提供缩略图、等比例压缩图和裁决图片
    """
    save_path = MEDIA_IMAGE_PATH
    quality = 85
    image_format = 'JPEG'
    max_disk_size = 2 * 1024 * 1024     # 最大占用磁盘空间大小
    max_size = (1080, 1440)             # 最大分辨率
    min_size = (320, 200)               # 最小分辨率
    postfix_format_dict = {'JPEG': 'jpg', 'PNG': 'png'}
    image_format_dict = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG'}
    INIT_NAMES = ('save_path', 'quality', 'image_format',
                  'max_disk_size', 'max_size', 'min_size')

    def __init__(self, image_name=None, image=None, **kwargs):
        if image:
            if isinstance(image, InMemoryUploadedFile):
                self.image = Image.open(image.file)
                image_format = image._name.split('.')[-1]
                file_name = make_no_repeat_image_name(image_name=image._name,
                                                      image_format=image_format)
                file_path = os.path.join(MEDIA_IMAGE_PATH, file_name)
                self.image.save(file_path,
                                self.image_format_dict[image_format.lower()],
                                quality=100)
                self.image = Image.open(file_path)

                # self.image.filename = image._name
                # self._size = image._size
                # self._content_type = image.content_type
                # self._charset = image.charset
                # self._content_type_extra = image.content_type_extra
                # self._field_name = image.field_name
            elif isinstance(image, BytesIO):
                self.image = Image.open(image)
                self.image.filename = '%s_%s.png' % (time.time(), make_random_char_and_number_of_string(8))
                self._size = self.image_size
            else:
                buff = BytesIO(image.data)
                self.image = Image.open(buff)
        else:
            self.image = Image.open(image_name)

        for key in kwargs:
            if key not in self.INIT_NAMES:
                raise TypeError('Params [%s] is incorrect.' % key)
            if key in ('max_size', 'min_size'):
                if not isinstance(kwargs[key], (tuple, list)):
                    raise TypeError('Params [max_size, min_size] must be tuple or list.')
            setattr(self, key, kwargs[key])

        # 关闭alpha 通道
        # if self.image_size > self.max_disk_size:
        #     self.close_alpha()
        self.close_alpha()

    @property
    def image_size(self):
        if getattr(self, '_size', None):
            return self._size

        self.image.fp.seek(0)
        buff = BytesIO(self.image.fp.read())
        disk_size = len(buff.read())
        buff.close()
        self._size = disk_size
        return disk_size

    @classmethod
    def image_disk_size(cls, new_image):
        new_image.fp.seek(0)
        buff = BytesIO(new_image.fp.read())
        disk_size = len(buff.read())
        buff.close()
        return disk_size

    def get_disk_size_for_bytes_io(self, bytes_instance):
        """
        获取BytesIo对象的大小
        :param bytes_instance: 
        :return: 
        """
        if not isinstance(bytes_instance, BytesIO):
            return Exception('Params type must be BytesIO instance.')

        bytes_instance.seek(0)
        disk_size = len(bytes_instance.read())
        bytes_instance.seek(0)
        return disk_size

    @classmethod
    def get_bytes_from_bytes_io(cls, bytes_instance):
        """
        获取BytesIO对象的二进制数据流
        :param bytes_instance: 
        :return: 
        """
        if isinstance(bytes_instance, InMemoryUploadedFile):
            bytes_instance = bytes_instance.file
        if not isinstance(bytes_instance, BytesIO):
            return Exception('Params type must be BytesIO instance.')

        bytes_instance.seek(0)
        bytes_buff = bytes_instance.read()
        bytes_instance.seek(0)
        return bytes_buff

    @classmethod
    def save_file_to_disk_for_in_memory_uploaded_file(cls, memory_file):
        """
        将InMemoryUploadedFile文件对象保存到磁盘上
        :param memory_file: 
        :return: 
        """
        if not isinstance(memory_file, InMemoryUploadedFile):
            return Exception('Params memory_file is incorrect.')

        file_path = os.path.join(MEDIA_IMAGE_PATH, make_no_repeat_image_name(memory_file._name))
        fp = open(file_path, 'wb')
        fp.write(memory_file.file.read())
        fp.close()
        return file_path

    @property
    def is_too_small(self):
        if self.image.size < self.min_size:
            return True

    @property
    def is_too_big(self):
        if self.max_size:
            if self.image.size > self.max_size:
                return True

    def compress(self, width=0, height=0, image_format=None, save_path=None):
        """
        缩略图
        返回：新图片的对象及名称（绝对目录）
        """
        if not save_path:
            save_path = self.save_path
        if not image_format:
            image_format = self.image_format
        file_name = '%s_%s.%s' % (self.image.filename.split('.', 1)[0],
                                  make_random_char_and_number_of_string(12),
                                  self.postfix_format_dict[image_format])
        file_path = os.path.join(save_path, file_name)
        new_image = copy.copy(self.image)
        try:
            new_image.thumbnail((width, height))
            new_image.save(file_path, image_format.upper())
        except Exception as e:
            return e
        return new_image, file_path

    def resize(self, ratio, quality=None, image_format=None, save_path=None):
        """
        等比例缩放
        返回：新图片的对象及名称（绝对目录）
        """
        if ratio >= 1:
            return self.image, self.image.filename

        if not quality:
            quality = self.quality
        if not save_path:
            save_path = self.save_path
        if not image_format:
            image_format = self.image_format
        origin_width, origin_height = self.image.size

        file_name = '%s_%s.%s' % (self.image.filename.split('.', 1)[0],
                                  make_random_char_and_number_of_string(12),
                                  self.postfix_format_dict[image_format])
        file_path = os.path.join(save_path, file_name)
        new_image = self.image.resize((int(origin_width*ratio), int(origin_height*ratio)),
                                      Image.ANTIALIAS)
        new_image.save(file_path, image_format.upper(), quality=quality)
        return new_image, file_path

    def resize_within_memory(self, ratio, quality=None, image_format=None):
        """
        等比例缩放
        返回：新图片的对象及名称（绝对目录）
        """
        if ratio >= 1:
            return self.image, self.image.filename

        if not quality:
            quality = self.quality
        if not image_format:
            image_format = self.image_format
        origin_width, origin_height = self.image.size

        new_image = self.image.resize((int(origin_width*ratio), int(origin_height*ratio)),
                                      Image.ANTIALIAS)
        io_buff = io.BytesIO()
        new_image.save(io_buff, format=image_format, quality=quality)
        memory_file = InMemoryUploadedFile(io_buff, None, self.image.filename,
                                           'image/jpeg', None, None)
        return memory_file

    def clip_resize(self, goal_width=0, goal_height=0, image_format=None,
                    quality=None, save_path=None):
        """
        裁决及等比例缩放 
        返回：新图片的对象及名称（绝对目录）
        """
        if not image_format:
            image_suffix = self.image.filename.split('.', 1)[1]
            image_format = self.image_format_dict[image_suffix.lower()]
        if not quality:
            quality = self.quality
        if not save_path:
            save_path = MEDIA_IMAGE_PATH

        file_name = '%s_%s.%s' % (self.image.filename.split('.', 1)[0],
                                  make_random_char_and_number_of_string(12),
                                  self.postfix_format_dict[image_format])
        file_path = os.path.join(save_path, file_name)

        origin_width, origin_height = self.image.size
        # if goal_width > origin_width or goal_height > origin_height:
        #     return False, ValueError('Params [goal_width] or [goal_height] is incorrect.')

        goal_ratio = goal_height / goal_width
        origin_ratio = origin_height / origin_width
        if origin_ratio >= goal_ratio:   # 原图过高
            height = origin_width * goal_ratio
            width = origin_width
            x = 0
            y = (origin_height - height) / 2
        else:  # 原图过宽
            height = origin_height
            width = origin_height / goal_ratio
            y = 0
            x = (origin_width - width) / 2

        box = (x, y, width + x, height + y)
        # 剪切图片
        new_image = self.image.crop(box)

        if height > goal_height or width > goal_width:
            # 压缩图片
            try:
                new_image = new_image.resize((int(goal_width), int(goal_height)), Image.ANTIALIAS)
            except Exception as e:
                return False, e

        new_image.save(file_path, image_format.upper(), quality=quality)
        new_image = Image.open(file_path)
        return new_image, file_path

    def clip_within_memory(self, goal_ratio=1, image_format=None, quality=None):
        """
        裁决
        返回：新图片的对象及名称（绝对目录）
        """
        if not image_format:
            image_format = self.image_format
        if not quality:
            quality = self.quality

        origin_height, origin_width = self.image.size
        origin_ratio = origin_height / origin_width
        if origin_ratio >= goal_ratio:   # 原图过高
            height = origin_width * goal_ratio
            width = origin_width
            x = 0
            y = (origin_height - height) / 2
        else:  # 原图过宽
            height = origin_height
            width = origin_height / goal_ratio
            y = 0
            x = (origin_width - width) / 2

        box = (x, y, width + x, height + y)
        # 剪切图片
        new_image = self.image.crop(box)

        io_buff = io.BytesIO()
        new_image.save(io_buff, format=image_format, quality=quality)
        disk_size = self.get_disk_size_for_bytes_io(io_buff)
        memory_file = InMemoryUploadedFile(file=io_buff,
                                           field_name=self._field_name,
                                           name=self.image.filename,
                                           content_type=self._content_type,
                                           size=disk_size,
                                           charset=self._charset,
                                           content_type_extra=self._content_type_extra)
        return memory_file

    def close_alpha(self):
        """
        如果图片格式是PNG，并且alpha通道是开启的，
        则将图片转化为JPEG格式，以此节省磁盘空间。
        """
        if self.image.mode == 'RGBA':
            # 使用白色来填充背景
            image_size = self.image.size
            image_filename = self.image.filename
            new_image = Image.new('RGBA', self.image.size, (255, 255, 255))
            new_image.paste(self.image,
                            (0, 0, self.image.size[0], self.image.size[1]),
                            self.image)

            tmp_image = Image.new('RGB', self.image.size, (255, 255, 255))
            tmp_image.paste(new_image,
                            (0, 0, self.image.size[0], self.image.size[1]),
                            new_image)
            # 保存图片
            new_file_name = make_no_repeat_image_name(self.image.filename.split('/')[-1], self.image.format)
            tmp_image.save(new_file_name, 'JPEG')
            image = Image.open(new_file_name)
            self.image = image

            # # 保存图片
            # io_buffer = BytesIO()
            # tmp_image.save(io_buffer, 'JPEG')
            # disk_size = self.get_disk_size_for_bytes_io(io_buffer)
            # memory_image = InMemoryUploadedFile(
            #     file=io_buffer,
            #     field_name=self._field_name,
            #     name=self.image.filename,
            #     content_type=self._content_type,
            #     size=disk_size,
            #     charset=self._charset,
            #     content_type_extra=self._content_type_extra)
            # self.image = Image.open(memory_image.file)
            # self.image.size = image_size
            # self.image.filename = image_filename


def send_mobile_message(mobile='', verifying_code=''):
    """
    发送手机短信验证码
    :param mobile: 手机号
    :param verifying_code: 验证码
    :return: True
    """
    client_id = '150805950'
    client_secret = '1A6D984B13D56EC82858F2C345583472'

    params_dict = {
        'client_id': client_id,
        'sign': hmac.new(client_secret.encode('utf8'), client_id.encode('utf8'), 'sha1').hexdigest(),
        'content': '验证码:%s, 您正在入驻精灵魔镜,请于5分钟内完成验证, 若非本人操作, 请忽略此短信。' % verifying_code,
        'type': 1,
        'mobile': mobile if mobile.startswith('86') else '86%s' % mobile
    }

    sms_url = 'http://xopen.ksmobile.com/sms/data'
    return http_requests.send_http_request(sms_url, params_dict, method='post')


def make_request_body_to_dict(body):
    """
    将request body数据转换成字典
    :param body: 
    :return: 
    """
    if not body:
        return {}

    if isinstance(body, bytes):
        body = body.decode('utf8')
    body_list = body.split('&')
    return {item.split('=')[0]: item.split('=')[1] for item in body_list}


def make_no_repeat_image_name(image_name=None, image_format='JPEG'):
    """
    生成不重名的图片名
    :param image_name: 
    :param image_format: 
    :return: 
    """
    if not image_name:
        image_name = '%s_%s.%s' % (int(time.time()), make_random_char_and_number_of_string(6), image_format)
    else:
        image_name = '%s_%s.%s' % (image_name.split('.')[0],
                                   make_random_char_and_number_of_string(6),
                                   image_name.split('.')[1])
    return image_name


def save_django_upload_file_to_disk(upload_file, save_path=MEDIA_IMAGE_PATH):
    """
    将django上传文件保存至服务器磁盘
    :param upload_file: 
    :param save_path: 
    :return: 
    """
    if not isinstance(upload_file, (InMemoryUploadedFile, TemporaryUploadedFile)):
        return Exception('Params [upload_file] data is incorrect.')

    no_repeat_name = '%s_%s.%s' % (upload_file.name.split('.', 1)[0],
                                   make_random_char_and_number_of_string(8),
                                   upload_file.name.split('.', 1)[1])
    file_name = os.path.join(save_path, no_repeat_name)
    with open(file_name, 'wb') as fp:
        for line in upload_file.readlines():
            fp.write(line)
    return file_name


class BaseUnzip(object):
    """
    解压缩文件
    """
    @classmethod
    def un_gz(cls, file_name):
        """
        解压缩.gz文件
        :param file_name: 
        :return: 解压缩后的文件路径
        """
        f_name = file_name.replace(".gz", "")
        # 创建gzip对象
        g_file = gzip.GzipFile(file_name)
        open(f_name, "wb").write(g_file.read())
        g_file.close()
        return f_name

    @classmethod
    def un_tar(cls, file_name):
        """
        解压缩.tar文件
        :param file_name: 
        :return: 解压缩后的文件路径
        """
        tar = tarfile.open(file_name)
        names = tar.getnames()
        dir_name = '%s_%s' % (file_name, make_random_char_and_number_of_string(12))
        if os.path.isdir(dir_name):
            pass
        else:
            os.mkdir(dir_name)
        # 由于解压后是许多文件，预先建立同名文件夹
        for name in names:
            tar.extract(name, dir_name)
        tar.close()
        return dir_name

    @classmethod
    def un_tar_gz(cls, file_name):
        """
        解压缩.tar.gz文件
        :param file_name: 
        :return: 解压缩后的文件路径
        """
        gz_file_name = cls.un_gz(file_name)
        return cls.un_tar(gz_file_name)

    @classmethod
    def un_rar(cls, file_name):
        """
        解压缩.rar文件
        :param file_name: 
        :return: 解压缩后的文件路径
        """
        rar = rarfile.RarFile(file_name)
        dir_name = '%s_%s' % (file_name, make_random_char_and_number_of_string(12))
        if os.path.isdir(dir_name):
            pass
        else:
            os.mkdir(dir_name)
        os.chdir(dir_name)
        rar.extractall()
        rar.close()

    @classmethod
    def un_zip(cls, file_name):
        """
        解压缩.zip文件
        :param file_name: 
        :return: 解压缩后的文件路径
        """
        zip_file = zipfile.ZipFile(file_name)
        dir_name = '%s_%s' % (file_name, make_random_char_and_number_of_string(12))
        if os.path.isdir(dir_name):
            pass
        else:
            os.mkdir(dir_name)
        for names in zip_file.namelist():
            zip_file.extract(names, dir_name)
        zip_file.close()
        return dir_name


class BaseTableFile(object):
    """
    工作表处理（excel、csv等）
    目前支持：excel、csv格式
    """
    execl_fields = None
    perfect_detail_form_class = None
    make_perfect_init_data_function = None

    def __init__(self, execl_fields, perfect_detail_form_class, make_perfect_init_data_function):
        self.execl_fields = execl_fields
        self.perfect_detail_form_class = perfect_detail_form_class
        self.make_perfect_init_data_function = make_perfect_init_data_function

    def read_content_for_csv(self, request, file_content):
        insert_data = []
        try:
            csv_file = io.TextIOWrapper(file_content)  # python 3 only
            # dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=";,")
            dialect = csv.Sniffer().sniff(csv_file.readline())
            csv_file.seek(0)
            reader = csv.reader(csv_file, dialect)
        except Exception as e:
            return e

        for init_data in list(reader)[1:]:
            perfect_content = []
            for item in init_data:
                if isinstance(item, (bytes, str)):
                    perfect_content.append(item.strip())
                else:
                    perfect_content.append(item)
            init_data = dict(zip(self.execl_fields, perfect_content))
            init_data = self.make_perfect_init_data_function(request, init_data)
            if isinstance(init_data, Exception):
                return init_data

            form = self.perfect_detail_form_class(init_data)
            if not form.is_valid():
                return Exception(form.errors)
            insert_data.append(form.cleaned_data)
        return insert_data

    def read_content_for_xls(self, request, file_content):
        insert_data = []
        try:
            wb = xlrd.open_workbook(
                filename=None, file_contents=file_content.read()
            )
        except Exception as e:
            return e
        table = wb.sheets()[0]
        row = table.nrows
        for i in range(1, row):
            content = table.row_values(i)
            perfect_content = []
            for item in content:
                if isinstance(item, (bytes, str)):
                    perfect_content.append(item.strip())
                else:
                    perfect_content.append(item)

            init_data = dict(zip(self.execl_fields, perfect_content))
            init_data = self.make_perfect_init_data_function(request, init_data)
            if isinstance(init_data, Exception):
                return init_data

            form = self.perfect_detail_form_class(init_data)
            if not form.is_valid():
                return Exception(form.errors)
            insert_data.append(form.cleaned_data)
        return insert_data
