# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from oauth2_provider.views import TokenView
from oauth2_provider.models import AccessToken
from django.utils.timezone import now
from django.http.response import HttpResponse

from users.serializers import (UserSerializer,
                               UserInstanceSerializer,
                               UserDetailSerializer,
                               IdentifyingCodeSerializer,
                               BatchUploadStoreFileTemplateSerializer,
                               StoreDetailSerializer,
                               StoreListSerializer,
                               AreaProvinceListSerializer,
                               AreaCityListSerializer,
                               BrandListSerializer)
from users.permissions import IsOwnerOrReadOnly
from users.models import (BusinessUser,
                          make_token_expire,
                          IdentifyingCode,
                          BatchUploadStoreFileTemplate,
                          AreaCity,
                          AreaProvince,
                          BusinessUserBind,
                          Group)
from users.forms import (CreateUserForm,
                         UpdateUserInfoForm,
                         SetPasswordForm,
                         SendIdentifyingCodeForm,
                         VerifyIdentifyingCodeForm,
                         BatchUploadStoreForm,
                         BusinessUserBatchCreateColumnDetailForm,
                         BatchUploadStoreFileTemplateForm,
                         CreateStoreUserForm,
                         UpdateStoreUserForm,
                         StoreDetailForm,
                         StoreListForm,
                         AreaProvinceListForm,
                         AreaCityListForm,
                         BrandListForm)

from horizon.views import (APIView,
                           FMDetailAPIView,
                           FMActionAPIView,
                           FMListAPIView)
from horizon import main
from horizon.http import status as fm_status

import copy
import urllib
import json


class UserNotLoggedAction(APIView):
    """
    create user API
    """
    post_form_class = CreateUserForm
    put_form_class = SetPasswordForm

    def verify_identifying_code(self, identifying_code):
        return True

    def get_object_by_username(self, username):
        return BusinessUser.get_object(**{'phone': username})

    def post(self, request, *args, **kwargs):
        """
        用户注册
        """
        form = CreateUserForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        result = self.verify_identifying_code(cld['identifying_code'])
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = BusinessUser.objects.create_user(**cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInstanceSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        忘记密码
        """
        form = SetPasswordForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        result = self.verify_identifying_code(cld['identifying_code'])
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object_by_username(cld['phone'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(instance)
        try:
            serializer.update_password(request, instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer_response = UserInstanceSerializer(instance)
        return Response(serializer_response.data, status=status.HTTP_206_PARTIAL_CONTENT)


class BrandList(FMListAPIView):
    """
    获取品牌列表
    """
    list_form_class = BrandListForm
    list_serializer_class = BrandListSerializer
    model_class = BusinessUser

    def get_instances_list(self, request, **kwargs):
        kwargs = {'role': 2, 'is_active': 1}
        return self.model_class.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取用户列表
        """
        return super(BrandList, self).post(request, *args, **kwargs)


class UserAction(generics.GenericAPIView):
    """
    update user API
    """
    put_form_class = UpdateUserInfoForm

    def get_object_of_user(self, request):
        return BusinessUser.get_object(**{'pk': request.user.id})

    def put(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        form = UpdateUserInfoForm(request.data, request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        obj = self.get_object_of_user(request)
        if isinstance(obj, Exception):
            return Response({'Detail': obj.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(obj)
        try:
            serializer.update_userinfo(request, obj, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer_response = UserInstanceSerializer(obj)
        return Response(serializer_response.data, status=status.HTTP_206_PARTIAL_CONTENT)


class UserDetail(generics.GenericAPIView):
    """
    用户详情
    """
    def get_user_info(self, user_id):
        return BusinessUser.get_detail(**{'id': user_id})

    def post(self, request, *args, **kwargs):
        detail = self.get_user_info(request.user.id)
        if isinstance(detail, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, detail.args)

        serializer = UserDetailSerializer(data=detail)
        if not serializer.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, serializer.errors)
        return fm_status.return_success_response(serializer.data)


class AuthLogin(TokenView):
    def set_old_token_to_expires(self, new_token):
        token = AccessToken.objects.get(token=new_token)
        kwargs = {'user': token.user, 'id__lt': token.id, 'expires__gt': now()}
        expires_token_list = AccessToken.objects.filter(**kwargs)
        for expires_token in expires_token_list:
            expires_token.expires = now()
            expires_token.save()

    def post(self, request, *args, **kwargs):
        response = super(AuthLogin, self).post(request, *args, **kwargs)
        response_dict = json.loads(response.content)

        if response.status_code == 200:
            # 单点登录
            self.set_old_token_to_expires(response_dict['access_token'])
            return_dict = {'code': 200,
                           'message': 'ok',
                           'data': response_dict}
        else:
            return_dict = {'code': response.status_code,
                           'message': response_dict}
        return HttpResponse(json.dumps(return_dict), 'text/plain')


class AuthLogout(generics.GenericAPIView):
    """
    用户认证：登出
    """
    def post(self, request, *args, **kwargs):
        make_token_expire(request)
        return Response(status=status.HTTP_200_OK)


class IdentifyingCodeAction(APIView):
    """
    send identifying code to a phone
    """
    post_form_class = SendIdentifyingCodeForm

    def verify_phone(self, cld):
        kwargs = {'phone': cld['phone']}
        instance = BusinessUser.get_object(**kwargs)
        if isinstance(instance, Exception):
            return False, 'The user of the phone number is not existed.'
        return True, None

    def make_perfect_init_data(self, **kwargs):
        identifying_code = main.make_random_number_of_string(str_length=6)
        init_data = {'phone': kwargs['phone'],
                     'identifying_code': identifying_code}
        return init_data

    def post(self, request, *args, **kwargs):
        """
        发送验证码
        """
        form = SendIdentifyingCodeForm(request.data)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        result, error_message = self.verify_phone(cld)
        if not result:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)

        init_data = self.make_perfect_init_data(**cld)
        serializer = IdentifyingCodeSerializer(data=init_data)
        if not serializer.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, serializer.errors)
        try:
            serializer.save()
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        # 发送到短线平台
        send_data = {'mobile': init_data['phone'],
                     'verifying_code': init_data['identifying_code']}
        main.send_mobile_message(**send_data)
        return fm_status.return_success_response()


class BatchUploadStoreAction(generics.GenericAPIView):
    """
    门店信息批量导入
    """
    post_form_class = BatchUploadStoreForm
    execl_fields = ('phone', 'area_province', 'area_city', 'address', 'business_name',
                    'hotline', 'permission_group', 'manager', 'email', 'backup_phone',)

    def make_perfect_init_data(self, request, validated_data):
        # 添加品牌
        validated_data['brand'] = request.user.brand
        # 获取city ID
        province = AreaProvince.get_object(province=validated_data['area_province'])
        try:
            _kwargs = {'province_id': province.id, 'city': validated_data['area_city']}
            city = AreaCity.get_object(**_kwargs)
        except:
            city_id = None
        else:
            city_id = city.id
        validated_data['city_id'] = city_id

        # 添加角色及权限组
        if validated_data['permission_group'].lower() not in ['senior', 'common']:
            validated_data['permission_group_id'] = None
        else:
            group_name = 'store_%s' % validated_data['permission_group'].lower()
            group_ins = Group.get_object(group_name=group_name)
            validated_data['permission_group_id'] = group_ins.id

        return validated_data

    def insert_to_db(self, request, file_content):
        insert_data = []
        # 目前支持xls和csv格式的文件

        base_table_file = main.BaseTableFile(execl_fields=self.execl_fields,
                                             perfect_detail_form_class=BusinessUserBatchCreateColumnDetailForm,
                                             make_perfect_init_data_function=self.make_perfect_init_data)
        if file_content._name.endswith('csv'):
            insert_data = base_table_file.read_content_for_csv(request, file_content)
        elif file_content._name.endswith('xlsx'):
            insert_data = base_table_file.read_content_for_xls(request, file_content)
        else:
            pass
        if isinstance(insert_data, Exception):
            return False, str(insert_data.args)

        return BusinessUser.batch_create_store_user(request, insert_data)

    def post(self, request, *args, **kwargs):
        """
        门店信息批量导入
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        form = BatchUploadStoreForm(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        result, error_message = self.insert_to_db(request, cld['store_file'])
        if not result:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)
        return fm_status.return_success_response()


class BatchUploadStoreFileTemplateDetail(FMDetailAPIView):
    """
    获取批量上传门店信息文件模板
    """
    detail_form_class = BatchUploadStoreFileTemplateForm
    detail_serializer_class = BatchUploadStoreFileTemplateSerializer
    model_class = BatchUploadStoreFileTemplate

    def get_instance(self, request, **kwargs):
        _kwargs = {'format': kwargs['format']}
        return self.model_class.get_object(**_kwargs)

    def post(self, request, *args, **kwargs):
        return super(BatchUploadStoreFileTemplateDetail, self).post(request, *args, **kwargs)


class StoreUserAction(FMActionAPIView):
    """
    门店用户创建、修改、删除等
    """
    post_form_class = CreateStoreUserForm
    post_serializer_class = UserSerializer
    put_form_class = UpdateStoreUserForm
    put_serializer_class = UserSerializer
    model_class = BusinessUser

    def is_request_data_valid(self, **kwargs):
        if 'city_id' in kwargs:
            city_instance = AreaCity.get_object(**{'id': kwargs['city_id']})
            if isinstance(city_instance, Exception):
                return False, city_instance.args
        return True, None

    def get_perfect_request_data(self, **kwargs):
        return kwargs

    def post(self, request, *args, **kwargs):
        """
        创建门店用户
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(StoreUserAction, self).post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        更新门店信息
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(StoreUserAction, self).put(request, *args, **kwargs)


class StoreDetail(FMDetailAPIView):
    """
    获取门店详细信息
    """
    detail_form_class = StoreDetailForm
    detail_serializer_class = StoreDetailSerializer
    model_class = BusinessUser

    def get_instance(self, request, **kwargs):
        return self.model_class.get_detail(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取门店详细信息
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(StoreDetail, self).post(request, *args, **kwargs)


class StoreList(FMListAPIView):
    """
    获取门店列表
    """
    list_form_class = StoreListForm
    list_serializer_class = StoreListSerializer
    model_class = BusinessUser

    def get_perfect_request_data(self, **kwargs):
        if 'province_id' in kwargs:
            city_instances = AreaCity.filter_objects(province_id=kwargs['province_id'])
            kwargs['city_id__in'] = [ins.id for ins in city_instances]
            if 'city_id' in kwargs:
                kwargs.pop('city_id')
        if 'permission_group' in kwargs:
            group_ins = Group.filter_objects()
            group_ins_dict = {ins.group_name: ins for ins in group_ins}
            kwargs['permission_group_id'] = group_ins_dict[kwargs['permission_group']].id
        return kwargs

    def get_instances_list(self, request, **kwargs):
        _kwargs = {'brand_user_id': request.user.id}
        store_instance = BusinessUserBind.filter_objects(**_kwargs)
        business_user_ids = [ins.business_user_id for ins in store_instance]

        kwargs['id__in'] = business_user_ids
        return self.model_class.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取门店列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(StoreList, self).post(request, *args, **kwargs)


class AreaProvinceList(FMListAPIView):
    """
    获取省份列表
    """
    list_form_class = AreaProvinceListForm
    list_serializer_class = AreaProvinceListSerializer
    model_class = AreaProvince

    def post(self, request, *args, **kwargs):
        """
        获取省份列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(AreaProvinceList, self).post(request, *args, **kwargs)


class AreaCityList(FMListAPIView):
    """
    获取某省份的城市列表
    """
    list_form_class = AreaCityListForm
    list_serializer_class = AreaCityListSerializer
    model_class = AreaCity

    def post(self, request, *args, **kwargs):
        """
        获取城市列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(AreaCityList, self).post(request, *args, **kwargs)

