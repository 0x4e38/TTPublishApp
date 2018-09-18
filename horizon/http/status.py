# -*- coding:utf8 -*-
from rest_framework import status
from rest_framework.response import Response

import copy

HTTP_200_OK = {
    'code': 200,
    'message': 'ok',
    'data': [],
}
HTTP_400_BAD_REQUEST = {
    'code': 400,
    'message': 'Bad Request!'
}
HTTP_401_UNAUTHORIZED = {
    'code': 401,
    'message': 'Authentication credentials were not provided.'
}
HTTP_403_FORBIDDEN = {
    'code': 403,
    'message': 'Forbidden',
}
HTTP_405_METHOD_NOT_ALLOWED = {
    'code': 405,
    'message': 'Method Not Allowed!'
}
HTTP_500_INTERNAL_SERVER_ERROR = {
    'code': 500,
    'message': 'Unlawful Request!'
}

STATUS_LIST = (HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
               HTTP_405_METHOD_NOT_ALLOWED, HTTP_500_INTERNAL_SERVER_ERROR)


def return_error_response(http_status, error_message=None):
    if http_status not in STATUS_LIST:
        return Response(HTTP_500_INTERNAL_SERVER_ERROR, status=status.HTTP_200_OK)

    response_error = copy.copy(http_status)
    if error_message:
        response_error['message'] = error_message
    return Response(response_error, status=status.HTTP_200_OK)


def return_success_response(data=None, **kwargs):
    response_success = copy.copy(HTTP_200_OK)
    response_success['data'] = data
    response_success.update(**kwargs)
    return Response(response_success, status=status.HTTP_200_OK)

