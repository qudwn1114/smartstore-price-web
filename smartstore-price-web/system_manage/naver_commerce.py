from django.conf import settings
from django.utils import timezone
from system_manage.models import Token

import time, datetime
import requests
import os
import bcrypt
import pybase64

# 환경 변수 읽기
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET

# 토큰 저장 (갱신 시 업데이트)
def save_token(access_token, expires_at):
    token, created = Token.objects.update_or_create(
        id=1,
        defaults={
            'access_token': access_token,
            'expires_at': expires_at,
        }
    )
    
# 저장된 토큰 불러오기
def load_token():
    try:
        token = Token.objects.get(id=1)
    except Token.DoesNotExist:
        return None
    
    remaining_time = token.expires_at - timezone.localtime()
    if remaining_time > datetime.timedelta(minutes=30):
        return token.access_token
    elif remaining_time > datetime.timedelta(seconds=0):
        print(f"[토큰 갱신 필요] 남은 시간: {remaining_time}")
        return None  # 갱신 필요
    else:
        return None  # 만료

def get_client_secret_sign(timestamp):
    # 밑줄로 연결하여 password 생성
    password = CLIENT_ID + "_" + str(timestamp)
    # bcrypt 해싱
    hashed = bcrypt.hashpw(password.encode('utf-8'), CLIENT_SECRET.encode('utf-8'))
    # base64 인코딩
    client_secret_sign = pybase64.standard_b64encode(hashed).decode('utf-8')
    return client_secret_sign


# 새로운 토큰 발급
def get_new_token():
    print('🚀 토큰 발급')
    now = timezone.localtime()
    ms = int(now.timestamp() * 1000)
    client_secret_sign = get_client_secret_sign(ms)
    
    TOKEN_URL = "https://api.commerce.naver.com/external/v1/oauth2/token"
    response = requests.post(TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "timestamp": ms,
        "grant_type": "client_credentials",
        "client_secret_sign":client_secret_sign,
        "type":"SELF"
    })
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        expires_in = token_data["expires_in"]
        expires_at = now + datetime.timedelta(seconds=expires_in) # 만료 시간 계산
        save_token(access_token, expires_at)  # DB에 저장
        return access_token
    else:
        print("토큰 발급 실패:", response.text)
        return None

# 유효한 토큰 가져오기
def get_valid_token():
    token = load_token()
    if token:
        return token
    return get_new_token()  # 기존 토큰이 없거나 만료되었으면 새로 발급