import datetime
import logging

import requests
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse

from common.views import BaseView


logger = logging.getLogger(__name__)


# Create your views here.
def login(request):
    """登录页面，使用模板渲染"""
    return render(request, 'login.html')

class ApiLogin(BaseView):
    def post(self, request):
        """点击登录按钮时调用此接口，通过比赛接口/api/auth/token验证用户名和密码，获取token"""
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 通过token接口验证用户名和密码
        api_json = self.api_login(request, username, password)
        logger.debug('登录获取token结果为：%s', api_json)
        if api_json.get('code') != 0 or not api_json.get('token'):
            # 登录失败展示报错信息
            return render(request, 'login.html', {'message': api_json['message']})

        # 登录成功跳转到配额展示页面
        response = HttpResponseRedirect('/website/quotas/')
        response.set_cookie('sessionid', request.session.session_key)
        return response


class ProductsView(BaseView):
    def get(self, request):
        api_json = self.api_get(request, '/products_folder')
        logger.debug('获取产品目录结果为：%s', api_json)
        products_folder = api_json['products_folder']

        api_json = self.api_get(request, '/products')
        logger.debug('获取产品列表结果为：%s', api_json)
        products = api_json['products']

        return render(request, 'products.html', {'products_folder': products_folder, 'products': products})


class QuotasView(BaseView):
    def get(self, request):
        api_json = self.api_get(request, '/quotas/current-user')
        return render(request, 'quotas.html', {'result': api_json['result']})


class DesktopsView(BaseView):
    def get(self, request):
        api_json = self.api_get(request, '/instances')
        logger.debug('获取服务桌面结果为：%s', api_json)
        desktops = api_json['result']

        api_json = self.api_get(request, '/quotas/current-user')
        quotas = api_json['result']['quotas']

        api_json = self.api_get(request, '/products')
        products = api_json['products']

        return render(request, 'desktops.html', {'desktops': desktops, 'products': products, 'quotas': quotas})


class ApiDesktopsView(BaseView):
    def post(self, request):
        display_name = request.POST.get('display_name')
        start_ip = request.POST.get('start_ip')
        description = request.POST.get('description')
        product_id = request.POST.get('product_id')
        memory_mb = request.POST.get('memory_mb')
        vcpu = request.POST.get('vcpu')
        system_gb = request.POST.get('system_gb')
        local_gb = request.POST.get('local_gb')

        api_json = self.api_post(request, '/instances', {
            'display_name': display_name,
            'start_ip': start_ip,
            'description': description,
            'product_id': product_id,
            'memory_mb': memory_mb,
            'vcpu': vcpu,
            'system_gb': system_gb,
            'local_gb': local_gb,
            'expand_enabled': False
        })
        logger.debug('创建服务桌面结果为：%s', api_json)
        return JsonResponse(api_json)
