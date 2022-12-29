import json

import requests

from django.http import JsonResponse
from django.views.generic import View

# Create your views here.
class BaseView(View):
    api_url = 'https://119.36.235.229:10110/api'

    def api_login(self, request, username: str, password: str) -> dict:
        """通过/api/auth/token接口验证用户名和密码"""
        response = requests.post(self.api_url + '/auth/token', json={'username': username, 'password': password}, verify=False)
        response_json = response.json()
        if response_json.get('code') == 0:
            token = response_json.get('token')
            request.session['username'] = username
            request.session['token'] = token
            request.session['refresh_token'] = response_json.get('refresh_token')
        return response_json

    def api_get(self, request, url_path: str) -> dict:
        token = request.session.get('token')
        if not token:
            return {'code': 10000, 'message': '用户未登录'}
        r = requests.get(self.api_url + url_path, headers={'Authorization': f'Bearer {token}'}, verify=False)
        api_json = r.json()
        return api_json

    def api_post(self, request, url_path: str, request_json: dict) -> dict:
        token = request.session.get('token')
        if not token:
            return JsonResponse({'code': 10000, 'message': '用户未登录'}, status=401)
        r = requests.post(self.api_url + url_path, headers={'Authorization': f'Bearer {token}'}, json=request_json, verify=False)
        api_json = r.json()
        return api_json


    def api_link(self, request, instance_id: str, username: str) -> dict:
        """通过用户输入连接服务器"""
        token = request.session.get('token')
        if not token:
            return {'code': 10000, 'message': '用户未登录'}
        response = requests.post(self.api_url + '/instance/connection', json={'instance_id': instance_id, 'username': username})
        response_json = response.json()
        return response_json