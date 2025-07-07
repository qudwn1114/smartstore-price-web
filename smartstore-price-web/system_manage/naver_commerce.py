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


def get_product_by_channel_product_no(access_token, channel_product_no):
    URL = "https://api.commerce.naver.com/external/v1/products/search"
    payload = {
        "searchKeywordType": "CHANNEL_PRODUCT_NO",
        "channelProductNos": [channel_product_no],
        "page": 1,
        "size": 1,
        "orderType": "NO",
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(URL, json=payload, headers=headers)  # 💡 JSON 자동 변환!

    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}, {response.text}")
    
    data = response.json()

    # 조회 결과가 없는 경우 예외 발생
    if not data.get("contents"):
        raise ValueError(f"상품을 찾을 수 없습니다. 채널 상품 번호: {channel_product_no}")
    
    # 상품 정보 추출
    channel_product_info = data["contents"][0]["channelProducts"][0]
    origin_product_no = channel_product_info["originProductNo"]
    name = channel_product_info["name"]

    return origin_product_no, name


def get_option_by_channel_product_no(access_token, channel_product_no):
    
    URL = f"https://api.commerce.naver.com/external/v2/products/channel-products/{channel_product_no}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(URL, headers=headers)  # 💡 JSON 자동 변환!

    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}, {response.text}")
    
    data = response.json()

    # 조회 결과가 없는 경우 예외 발생
    origin_product = data.get("originProduct")
    if not origin_product:
        raise ValueError(f"상품을 찾을 수 없습니다. 채널 상품 번호: {channel_product_no}")

    # detailAttribute 가져오기
    detail_attribute = origin_product.get("detailAttribute")
    if not detail_attribute:
        raise ValueError(f"상품 상세 정보를 찾을 수 없습니다. 채널 상품 번호: {channel_product_no}")

    # 조회 결과가 없는 경우 예외 발생
    option_info = detail_attribute.get("optionInfo")
    if not option_info:
        option_data = {
            "option_group_quantity": 0,
            "option_name1": None,
            "option_name2": None,
            "option_name3": None,
            "options": []
        }
        return option_data
    
    group_names = option_info.get("optionCombinationGroupNames", {})
    option_combinations = option_info.get("optionCombinations", [])
    option_data = {
        "option_group_quantity": len(group_names),
        "option_group_name1": group_names.get("optionGroupName1", None),
        "option_group_name2": group_names.get("optionGroupName2", None),
        "option_group_name3": group_names.get("optionGroupName3", None),
        "options": []
    }

    for option in option_combinations:
        option_data["options"].append({
            "option_id": option.get("id"),
            "option_name1": option.get("optionName1", None),
            "option_name2": option.get("optionName2", None),
            "option_name3": option.get("optionName3", None),
            "price": option.get("price", 0)
        })

    return option_data