from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import transaction

from system_manage.decorators import permission_required
from system_manage.naver_commerce import get_valid_token, get_product_by_channel_product_no, get_option_by_channel_product_no
from system_manage.models import GoldPrice, GoldPriceHistory, CrawlTarget, Product, GroupOption

from decimal import Decimal
import logging, traceback

@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def create_product(request):
    channel_product_no = int(request.POST['channel_product_no'])
    gold = Decimal(request.POST['gold'])
    labor_cost = int(request.POST['labor_cost'])
    sub_cost = int(request.POST['sub_cost'])
    markup_rate = Decimal(request.POST['markup_rate'])

    access_token = get_valid_token()
    if not access_token:
        return JsonResponse({'message': 'Access token is not available.'}, status=400)
    try:
        gold_price = GoldPrice.objects.get(id=1).price
    except GoldPrice.DoesNotExist:
        return JsonResponse({'message': 'Gold price not found.'}, status=400)
    if Product.objects.filter(channel_product_no=channel_product_no).exists():
        return JsonResponse({'message': '이미 등록된 상품 번호입니다.'}, status=400)
    try:
        origin_product_no, product_name = get_product_by_channel_product_no(access_token=access_token, channel_product_no=channel_product_no)
        options = get_option_by_channel_product_no(access_token, channel_product_no)  # 옵션 조회 추가
        print(f"상품 조회 성공: {origin_product_no}, {product_name}")
        # 이후 추가 로직 (DB 저장 등)
    except ValueError as e:
        return JsonResponse({'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'message': f'API 요청 에러: {e}'}, status=400)
    
    group_option_data = []
    for opt in options['options']:
        group_option_data.append({
            "channel_product_no": channel_product_no,
            "option_id": opt['option_id'],
            "option_name1": opt.get('option_name1'),
            "option_name2": opt.get('option_name2'),
            "option_name3": opt.get('option_name3'),
            "gold": 0,
            "sub_cost": opt.get('price'),
            "markup_rate": 1,
            "price": opt.get('price')
        })

    try:
        with transaction.atomic():
            logger = logging.getLogger('my')
            # 판매가 계산
            unit_cost = (gold_price * gold) + labor_cost + sub_cost
            raw_price = unit_cost * markup_rate 
            # 천원 단위 반올림
            price = round(raw_price / 1000) * 1000
            product = Product.objects.create(
                origin_product_no=origin_product_no,
                channel_product_no=channel_product_no,
                name=product_name,
                price=price,
                gold=gold,
                labor_cost=labor_cost,
                sub_cost=sub_cost,
                markup_rate=markup_rate,
                option_group_quantity=options['option_group_quantity'],
                option_group_name1=options.get('option_group_name1'),
                option_group_name2=options.get('option_group_name2'),
                option_group_name3=options.get('option_group_name3'),
                option_group_flag=False  # 옵션 그룹 업데이트 여부
            )
            GroupOption.objects.bulk_create([
                GroupOption(
                    product=product,
                    option_id=o['option_id'],
                    option_name1=o['option_name1'] or None,
                    option_name2=o['option_name2'] or None,
                    option_name3=o['option_name3'] or None,
                    gold=o['gold'],
                    sub_cost=o['sub_cost'],
                    markup_rate=o['markup_rate'],
                    price=o['price'],
                ) for o in group_option_data
            ])
    except:
        logger.error(traceback.format_exc())
        return JsonResponse({'message': '상품 등록 중 오류가 발생했습니다.'}, status=400)
                  
    return JsonResponse({'message': '상품이 등록 되었습니다.'}, status=201)


@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def edit_product(request):
    product_id = int(request.POST['product_id'])
    gold = Decimal(request.POST['gold'])
    labor_cost = int(request.POST['labor_cost'])
    sub_cost = int(request.POST['sub_cost'])
    markup_rate = Decimal(request.POST['markup_rate'])

    try:
        gold_price = GoldPrice.objects.get(id=1).price
    except GoldPrice.DoesNotExist:
        return JsonResponse({'message': 'Gold price not found.'}, status=400)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found.'}, status=400)
    
    unit_cost = (gold_price * gold) + labor_cost + sub_cost
    raw_price = unit_cost * markup_rate 
    # 천원 단위 반올림
    price = round(raw_price / 1000) * 1000

    try:
        with transaction.atomic():
            product.gold = gold
            product.labor_cost = labor_cost
            product.sub_cost = sub_cost
            product.markup_rate = markup_rate
            product.price = price
            product.save()
    except:
        return JsonResponse({'message': 'Error occurred while updating product.'}, status=400)

    return JsonResponse({'message': '업데이트 되었습니다.'}, status=200)


@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def delete_product(request):
    product_id = int(request.POST['product_id'])
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found.'}, status=400)
    
    try:
        with transaction.atomic():
            product.delete()
    except:
        return JsonResponse({'message': 'Error occurred while deleting product.'}, status=400)

    return JsonResponse({'message': '삭제 되었습니다.'}, status=200)

@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def bulk_update_product(request):
    don = int(request.POST['don'])
    try:
        gold_price = GoldPrice.objects.get(id=1).price
    except GoldPrice.DoesNotExist:
        return JsonResponse({'message': 'Gold price not found.'}, status=400)
    if don != int(gold_price * 3.75):
        return JsonResponse({'message': '1돈의 금액이 일치하지 않습니다. 새로고침 후 다시 시도해주세요.'}, status=400)
    products = Product.objects.all()
    group_options = GroupOption.objects.all()
    now = timezone.now()
    try:
        with transaction.atomic():
            for product in products:
                unit_cost = (gold_price * product.gold) + product.labor_cost + product.sub_cost
                raw_price = unit_cost * product.markup_rate
                price = round(raw_price / 1000) * 1000
                product.price = price
                product.updated_at = now
            Product.objects.bulk_update(products, ['price', 'updated_at'])

            # 옵션 가격 업데이트
            for group_option in group_options:
                unit_cost = gold_price * group_option.gold + group_option.sub_cost
                raw_price = unit_cost * group_option.markup_rate
                price = round(raw_price / 1000) * 1000
                if abs(price) > group_option.product.price * 0.5:
                    raise ValueError(f"{group_option.product.name} 옵션의 가격이 상품 가격의 50%를 초과합니다.")
                group_option.price = price
                group_option.updated_at = now
            GroupOption.objects.bulk_update(group_options, ['price', 'updated_at'])
    except ValueError as e:
        return JsonResponse({'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'message': f'업데이트 실패 : {e}'}, status=400)
    return JsonResponse({'message': '일괄 적용 되었습니다.'}, status=200)
