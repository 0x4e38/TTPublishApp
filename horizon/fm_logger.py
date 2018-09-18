# -*- coding:utf8 -*-

from django.conf import settings
import copy
import time
import datetime
import collections
import json
import logging
import os


LOG_FILE_PATH = '/var/www/log/business/'


class BaseLogger(object):
    def __init__(self, logger_name='API LOG', level='DEBUG', file_name=None):
        self.logger = logging.getLogger(logger_name)
        self.formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s',
                                           '%Y-%m-%d %H:%M:%S', )
        self.level = level

        if not file_name.startswith('/'):
            file_name = os.path.join(LOG_FILE_PATH, file_name)

        save_path = os.path.dirname(file_name)
        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        self.file_name = file_name
        file_handler = logging.FileHandler(self.perfect_file_name)
        file_handler.setFormatter(self.formatter)
        self.file_handle = file_handler
        self.logger.addHandler(file_handler)
        self.logger.setLevel(level=level)

    def debug(self, message, *args, **kwargs):
        return self.perfect_logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        return self.perfect_logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        return self.perfect_logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        return self.perfect_logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        return self.perfect_logger.critical(message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        return self.perfect_logger.exception(message, *args, **kwargs)

    def log(self, level, message, *args, **kwargs):
        return self.perfect_logger.log(level, message, *args, **kwargs)

    @property
    def date_of_today(self):
        return datetime.date.today().strftime('%Y%m%d')

    @property
    def perfect_file_name(self):
        if self.date_of_today not in self.file_name:
            file_name_list = self.file_name.split('.')
            if len(file_name_list) == 2:
                perfect_fname = '%s.%s.%s' % (file_name_list[0],
                                              self.date_of_today,
                                              file_name_list[1])
            else:
                file_name_list[2] = self.date_of_today
                perfect_fname = '.'.join(file_name_list)
            return perfect_fname
        else:
            return self.file_name

    @property
    def perfect_logger(self):
        if self.perfect_file_name != self.file_name:
            self.file_name = self.perfect_file_name
            self.logger.removeHandler(self.file_handle)
            self.file_handle = logging.FileHandler(self.perfect_file_name)
            self.file_handle.setLevel(level=self.level)
            self.file_handle.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handle)
        return self.logger
