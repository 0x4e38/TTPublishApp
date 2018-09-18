# -*- coding:utf8 -*-
import hashlib
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from rest_framework import status
import json
import copy

from horizon.fm_logger import BaseLogger
from horizon import main
from horizon.middleware.forms import PublicParamsForm
from FMBusinessApp import config


RETURN_UNLAWFUL = {
    'status': 500,
    'msg': 'Unlawful request!'
}


class CommonMiddleware(MiddlewareMixin):
    """
    通用中间件：用于校验request请求的头部信息是否正确，
    用来确认request请求是否是合法的并且没有被修改过。
    校验标准：根据request body里的参数（经过排序）和随机字符串（提前指定）来生成MD5值，
            并和request header里的Authorization字段进行比较，如果一致，则是有效请求，
            如果不一致，则判定为非法请求或已经被篡改的请求。
    """
    SECRET_KEY = """SVfLS7/la-!%,o{H=i;&wAf@T!magic_mirror"""
    logger = BaseLogger(level='DEBUG', file_name='request_and_response.log')

    def process_request(self, request):
        """
        检验request header信息
        """
        return None

        # return_unlawful = copy.copy(RETURN_UNLAWFUL)
        # if 'AUTHORIZATION' not in request.META:
        #     return HttpResponse(json.dumps(return_unlawful), 'text/plain')
        #
        # http_body = json.loads(request.body)
        # http_authorization = request.META['AUTHORIZATION']
        # sign_string = main.make_sign_with_hmacmd5(http_body, self.SECRET_KEY)
        # if http_authorization.upper() != sign_string:
        #     return HttpResponse(json.dumps(return_unlawful), 'text/plain')
        #
        # form = PublicParamsForm(http_body)
        # if not form.is_valid():
        #     return_unlawful['msg'] = form.errors
        #     return HttpResponse(json.dumps(return_unlawful), 'text/plain')
        #
        # # 添加请求日志
        # # pass
        #
        # return None

    def process_response(self, request, response):
        """
        Calculate the ETag, if needed.

        When the status code of the response is 404, it may redirect to a path
        with an appended slash if should_redirect_with_slash() returns True.
        """
        if response.status_code != 200:
            try:
                message = json.loads(response.content)
            except:
                message = ''
            return_dict = {'code': response.status_code,
                           'message': message}
            return HttpResponse(json.dumps(return_dict), 'text/plain')

        # 本地开发环境、测试环境记录访问日志，线上环境不记录访问日志
        if config.ENVIRONMENT != 'PRODUCT':
            # 记录请求处理结果日志
            params_post = dict(getattr(request, 'POST', {}))
            params_get = dict(getattr(request, 'GET', {}))
            try:
                params_body = main.make_request_body_to_dict(getattr(request, 'body', ''))
            except:
                params_body = {}

            logger_dict = {'request_url': request.path,
                           'request_post': params_post,
                           'request_get': params_get,
                           'request_body': params_body,
                           'request_header': request.META,
                           'response_status': response.status_code,
                           'response_content': response.content.decode('utf8')}
            self.logger.info(str(logger_dict))

        return response
