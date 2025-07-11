from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import transaction

from system_manage.decorators import permission_required
from system_manage.naver_commerce import get_valid_token, product_multi_update, option_stock
from system_manage.models import GoldPrice, Product, GroupOption, ApplyTaskHistory

import time, logging, traceback

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
    
    access_token = get_valid_token()
    products = [
        {
            "originProductNo": product.origin_product_no,
            "salePrice": product.price
        }
    ]
    try:
        product_multi_update(access_token=access_token, products=products)
    except Exception as e:
        return JsonResponse({'message': 'API 요청 에러", f"⚠️ 오류 내용: {e}'}, status=400)
    
    group_options = product.options.all()
    if product.option_group_flag and group_options.exists():
        option_combinations = []
        for group_option in group_options:
            option_data = {
                "id": group_option.option_id,  # 첫 번째 컬럼을 ID로 사용
                "stockQuantity": 999,  # 항상 999로 설정
                "price": group_option.price,  # 가격 컬럼(인덱스에 맞게 조정)
                "usable": True  # 항상 True로 설정
            }
            option_combinations.append(option_data)
        try:
            option_stock(access_token=access_token, origin_product_no=product.origin_product_no, sale_price=product.price, option_combinations=option_combinations)
        except Exception as e:
            return JsonResponse({'message': 'API 요청 에러", f"⚠️ 오류 내용: {e}'}, status=400)
        
        return JsonResponse({'message': '상품 & 옵션 가격이 업데이트 되었습니다.'}, status=200)

    return JsonResponse({'message': '상품 가격이 업데이트 되었습니다.'}, status=200)


@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def bulk_apply_product(request):
    logger = logging.getLogger('my')
    apply_task_id = request.POST['apply_task_id']
    try:
        apply_task = ApplyTaskHistory.objects.get(pk=apply_task_id)
    except:
        return JsonResponse({'message': 'Apply Task not found.'}, status=400)
    # 1단계
    apply_task.progress = 10
    apply_task.status_message = '상품을 불러오고 있습니다.'
    apply_task.save()
    products = Product.objects.filter(option_group_flag=False)
    option_products = Product.objects.filter(option_group_flag=True)
    time.sleep(0.5)

    # 2단계
    apply_task.progress = 30
    apply_task.status_message = '데이터 가공 중 입니다.'
    apply_task.save()
    products = [{"originProductNo": p.origin_product_no, "salePrice": p.price} for p in products]
    options = []
    for i in option_products:
        option_combinations = [
            {"id": o.option_id, "stockQuantity": 999, "price": o.price, "usable": True}
            for o in i.options.all()
        ]
        options.append({
            "origin_product_no": i.origin_product_no,
            "sale_price": i.price,
            "option_combinations": option_combinations
        })
    time.sleep(0.5)

    total_steps = len(products) + len(options)# 전체 제품 수
    completed_steps = 0
    access_token = get_valid_token()

    chunk_size = 100
    for i in range(0, len(products), chunk_size):
        product_chunk = products[i:i + chunk_size]
        product_multi_update(access_token=access_token, products=product_chunk)
        completed_steps += len(product_chunk)
        percent = int(completed_steps / total_steps * 60) 
        apply_task.progress = 30 + percent
        apply_task.status_message = f"일반 상품 업데이트 중 입니다. ({completed_steps}/{len(products)})"
        apply_task.save()
        time.sleep(0.5)

    # (3) 옵션 업데이트 (네이버 API)
    for idx, opt in enumerate(options):
        try:
            option_stock(
                access_token=access_token,
                origin_product_no=opt["origin_product_no"],
                sale_price=opt["sale_price"],
                option_combinations=opt["option_combinations"]
            )
        except:
            logger.error(traceback.format_exc())
            return JsonResponse({'message': 'API 요청 에러", f"⚠️ 오류 내용: {e}'}, status=400)

        completed_steps += 1
        percent = int(completed_steps / total_steps * 70)
        apply_task.progress = 30 + percent
        apply_task.status_message = f"옵션 상품 업데이트 중 입니다. ({idx+1}/{len(options)})"
        apply_task.save()
        time.sleep(0.5)

    apply_task.status_message = '작업이 완료되었습니다.'
    apply_task.progress = 100
    apply_task.status = True
    apply_task.save()
    time.sleep(0.5)
        
    return JsonResponse({'message': '업데이트 되었습니다.'}, status=200)