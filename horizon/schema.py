# -*- coding:utf8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
from rest_framework.permissions import AllowAny
from rest_framework.schemas import SchemaGenerator
from rest_framework.schemas.generators import LinkNode, insert_into
from rest_framework.renderers import *
from rest_framework_swagger import renderers
from rest_framework.response import Response
from rest_framework import generics
from django.utils.six.moves.urllib import parse as urlparse
from rest_framework.compat import coreapi, coreschema
from horizon.forms.fields import *
from django.forms.fields import *
from rest_framework.views import APIView


class MySchemaGenerator(SchemaGenerator):
    def get_link(self, path, method, view, base_url):
        fields = view.schema.get_path_fields(path, method)

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = view.schema.get_encoding(path, method)
        else:
            encoding = "multipart/form-data"

        description = view.schema.get_description(path, method)

        if base_url and path.startswith('/'):
            path = path[1:]

        return coreapi.Link(
            url=urlparse.urljoin('', path),
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=description
        )

    def get_links(self, request=None):
        links = LinkNode()

        paths = []
        view_endpoints = []
        for path, method, callback in self.endpoints:
            view = self.create_view(callback, method, request)
            path = self.coerce_path(path, method, view)
            paths.append(path)
            view_endpoints.append((path, method, view))

        # Only generate the path prefix for paths that will be included
        if not paths:
            return None
        prefix = self.determine_path_prefix(paths)

        child_path = self.url.split('com')[1][:-1]
        for path, method, view in view_endpoints:
            if not self.has_view_permissions(path, method, view):
                link = self.get_link(path, method, view, base_url='')
            else:
                link = view.schema.get_link(path, method, base_url='')
            link._url = child_path + link._url
            link._encoding = "multipart/form-data"

            # 添加下面这一行方便在views编写过程中自定义参数.
            link._fields += self.get_core_fields(view, method)
            subpath = path[len(prefix):]
            keys = self.get_keys(subpath, method, view)
            # from rest_framework.schemas.generators import LinkNode, insert_into
            insert_into(links, keys, link)
        return links

    def format_field(self, value):
        dic = {"type": ""}
        error_messages = value.error_messages
        description = ""
        if isinstance(value, CharField):
            max_length = value.max_length
            min_length = value.min_length
            if max_length:
                description += "max_length is %d " % max_length
            if min_length:
                description += "min_length is %d " % min_length
            dic["type"] = "string"
            dic["schema"] = coreschema.String(title='', description=description, min_length=min_length, max_length=max_length)
        elif isinstance(value, IntegerField):
            min_value = value.min_value
            max_value = value.max_value
            if max_value:
                description += "max_value is %d " % max_value
            if min_value:
                description += "min_value is %d " % min_value
            dic["schema"] = coreschema.Integer(title='', description=description, minimum=min_value, maximum=max_value)
            dic["type"] = "integer"
        elif isinstance(value, ChoiceField):
            choices = value._choices
            description += str(choices).strip('[]')
            choice_list = set([k[0] for k in choices])
            dic["type"] = "enum"
            dic["schema"] = coreschema.Enum(title='', description=description, enum=choice_list)
        else:
            dic["type"] = "string"
            dic["schema"] = coreschema.String(title='', description=description)
        dic["description"] = description + value.help_text
        return dic

    # 从类中取出我们自定义的参数, 交给swagger 以生成接口文档.
    def get_core_fields(self, view, method):
        form_class_str = ""
        if method == "PUT":
            form_class_str = ("put_form_class", )
        elif method == "POST":
            form_class_str = ("post_form_class", "detail_form_class", "list_form_class")
        elif method == "DELETE":
            form_class_str = ("delete_form_class", )

        fn = None
        for class_name in form_class_str:
            fn = getattr(view.__class__, class_name, None)
            if fn:
                break
        fields = []

        if not self.has_view_permissions("", method, view):
            fields.append(DocParam("Authorization"))
        if fn:
            for key, value in fn.declared_fields.items():
                dic = self.format_field(value)
                field = coreapi.Field(
                    name=key,
                    location="form",
                    type=dic["type"],
                    required=value.required,
                    schema=dic['schema']
                )
                # fields.append(self.format_field(view.__class__, key))
                fields.append(field)
        return tuple(fields)


class SwaggerSchemaView(APIView):
    _ignore_model_permissions = True
    exclude_from_schema = True

    permission_classes = [AllowAny]
    renderer_classes = [
        CoreJSONRenderer,
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
    ]

    def get(self, request):
        generator = MySchemaGenerator(title='APIs',
                                      description='''精灵魔镜商户后台接口文档''',
                                      url='http://test-fairy.cmcm.com/api-bz')
        schema = generator.get_schema(request=request)
        return Response(schema)


def DocParam(name="default", location="header",
             required=True, description=None, type="string",
             *args, **kwargs):
    return coreapi.Field(name=name, location=location,
                         required=required, description=description,
                         type=type)

