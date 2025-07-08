from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import transaction

from system_manage.decorators import permission_required
from system_manage.naver_commerce import get_valid_token, get_product_by_channel_product_no, get_option_by_channel_product_no
from system_manage.models import GoldPrice, Product, GroupOption, ApplyTaskHistory

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options

from decimal import Decimal
import logging, traceback

@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def create_apply_task(request):
    apply_task = ApplyTaskHistory.objects.create(
        progress=0,
        status=False,
        status_message='작업 준비 중 입니다.'
    )
    return JsonResponse({'message': apply_task.status_message, 'apply_task_id':apply_task.pk}, status=201)

@require_http_methods(["GET"])
@permission_required(raise_exception=True)
def polling_apply_task(request, *args, **kwargs):
    apply_task_id = kwargs.get('apply_task_id')
    try:
        apply_task = ApplyTaskHistory.objects.get(pk=apply_task_id)
    except:
        return JsonResponse({'message': 'Apply Task not found.'}, status=400)
    
    return JsonResponse({'message': apply_task.status_message, 'progress':apply_task.progress}, status=200)

@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def apply_product(request):
    product_id = int(request.POST['product_id'])
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found.'}, status=400)
    try:
        gold_price = GoldPrice.objects.get(id=1).price
    except GoldPrice.DoesNotExist:
        return JsonResponse({'message': 'Gold price not found.'}, status=400)
    
    return JsonResponse({'message': '업데이트 되었습니다.'}, status=200)


@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def bulk_apply_product(request):
    apply_task_id = request.POST['apply_task_id']
    try:
        apply_task = ApplyTaskHistory.objects.get(pk=apply_task_id)
    except:
        return JsonResponse({'message': 'Apply Task not found.'}, status=400)
    
    import time
    apply_task.progress = 10
    apply_task.status_message = '상품을 불러오고 있습니다.'
    apply_task.save()

    time.sleep(5)
    apply_task.progress = 50
    apply_task.status_message = '일반 상품 업데이트 중 입니다.'
    apply_task.save()
    time.sleep(5)
    apply_task.progress = 70
    apply_task.status_message = '옵션 상품 업데이트 중 입니다.'
    apply_task.save()
    time.sleep(5)
    apply_task.status_message = '작업이 완료되었습니다.'
    apply_task.progress = 100
    apply_task.status = True
    apply_task.save()
        
    return JsonResponse({'message': '업데이트 되었습니다.'}, status=200)