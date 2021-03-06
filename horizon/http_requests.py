# -*- coding:utf8 -*-
import requests
import urllib3
from rest_framework.views import View


def send_http_request(access_url, access_params, method='get',
                      content_type='application/json', charset='UTF-8', **kwargs):
    """
    发送http request请求
    """
    # if isinstance(access_params, dict):
    #     access_params = urllib3.request.urlencode(access_params)

    if method not in View.http_method_names:
        return TypeError("Http request cannot confirm the %s method!" % method)

    headers = None
    if 'headers' in kwargs:
        headers = {key: value for key, value in kwargs['headers'].items()}
    else:
        if 'add_header' in kwargs:
            headers = {'Content-Type': '%s; %s' % (content_type, charset)}
            for key, value in kwargs['add_header'].items():
                headers[key] = value

    kwargs = {'headers': headers} if headers else {}
    handle = getattr(requests, method)
    try:
        results = handle(access_url, access_params, **kwargs)
    except Exception as e:
        return e
    return results
