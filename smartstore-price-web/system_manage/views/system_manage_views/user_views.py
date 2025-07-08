from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.core.validators import validate_email
from django.core.exceptions  import ValidationError
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from system_manage.decorators import permission_required
from system_manage.views.system_manage_views.auth_views import validate_username, validate_phone, validate_birth, validate_password
import json, uuid


class UserDetailView(View):
    '''
        회원 상세
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {} 
        context['active_menu1'] = 'user'
        pk = kwargs.get('pk')
        data = get_object_or_404(User, pk=pk)
        context['data'] = data

        return render(request, 'user_manage/user_detail.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            data = User.objects.get(pk=pk)
        except:
            return JsonResponse({'message': '데이터 오류'}, status=400)

        membername = request.POST['membername'].strip()
        if membername == '':
            return JsonResponse({'message': '이름을 입력해주세요.'}, status=400)
        birth = request.POST['birth']
        if not validate_birth(birth):
            return JsonResponse({'message': '생년월일 형식 오류'}, status=400)
        email = request.POST['email'].strip()
        if email:
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'message': '이메일 형식 오류'}, status=400)
            if User.objects.filter(email=email).exclude(pk=pk).exists():
                return JsonResponse({'message': '이미 사용중인 이메일입니다.'}, status=400)
        else:
            email = None
        gender = request.POST['gender']
        if gender:
            if gender not in ['MALE', 'FEMALE']:
                return JsonResponse({'message': '성별 형식 오류'}, status=400)    
        else:
            gender = None

        try:
            with transaction.atomic():
                data.profile.membername = membername
                data.profile.birth = birth
                data.profile.gender = gender
                data.email = email or ""
                data.save()
        except Exception as e:
            print(e)
            return JsonResponse({'message': '저장 오류'}, status=400)

        return JsonResponse({'message' : '저장 되었습니다.'},  status = 202)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        request.PUT = json.loads(request.body)
        # 받은 데이터로 카테고리 업데이트
        data_type = request.PUT.get('data_type')
        try:
            data = User.objects.get(id=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        if data_type == 'PASSWORD':
            new_password1 = request.PUT.get('new_password1')
            new_password2 = request.PUT.get('new_password2')
            if new_password1 != new_password2:
                return JsonResponse({'message':'새로운 비밀번호가 일치하지 않습니다.'}, status = 400)
            if not validate_password(new_password1):
                return JsonResponse({'message': '비밀번호는 8~16자리 영숫자 포함이어야합니다.'}, status=400)
            if data == request.user:
                data = request.user
            data.set_password(new_password1)
            data.save()
            update_session_auth_hash(request, data)
        else:
            return JsonResponse({"message": "데이터 타입 오류"},status=400)        
        return JsonResponse({'message' : '업데이트 되었습니다.'},  status = 200)