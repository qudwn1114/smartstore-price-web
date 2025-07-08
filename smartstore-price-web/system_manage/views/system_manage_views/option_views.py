from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import transaction

from system_manage.decorators import permission_required
from system_manage.naver_commerce import get_valid_token, get_option_by_channel_product_no
from system_manage.models import GoldPrice, GoldPriceHistory, CrawlTarget, Product, GroupOption

from decimal import Decimal
import json


@require_http_methods(["GET"])
@permission_required(raise_exception=True)
def get_option(request, *args, **kwargs):
    product_id = kwargs.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found.'}, status=400)
    option_group_names = []
    if product.option_group_name1:
        option_group_names.append(product.option_group_name1)
    if product.option_group_name2:
        option_group_names.append(product.option_group_name2)
    if product.option_group_name3:
        option_group_names.append(product.option_group_name3)

    options = product.options.all().values(
        'id', 'option_id', 'option_name1', 'option_name2', 'option_name3', 'gold', 'sub_cost', 'markup_rate', 'price')

    return JsonResponse({'product_id':product.pk, 'option_group_names': option_group_names, 'options': list(options), 'option_group_flag': product.option_group_flag}, status=200)


@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def edit_option(request, *args, **kwargs):
    product_id = kwargs.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found.'}, status=400)
    request.POST = json.loads(request.body)
    options = request.POST.get('options', [])
    flag = request.POST.get('option_group_flag', False)
    if not options:
        return JsonResponse({'message': '업데이트 할 내용이 없습니다.'}, status=400)
    try:
        gold_price = GoldPrice.objects.get(id=1).price
    except GoldPrice.DoesNotExist:
        return JsonResponse({'message': 'Gold price not found.'}, status=400)
    try:
        with transaction.atomic():
            for option in options:
                option_id = option.get('id')
                try:
                    group_option = GroupOption.objects.get(id=option_id, product=product)
                except GroupOption.DoesNotExist:
                    return JsonResponse({'message': f'Option with id {option_id} not found.'}, status=400)
                gold = Decimal(option.get('gold', group_option.gold))
                sub_cost = int(option.get('sub_cost', group_option.sub_cost))
                markup_rate = Decimal(option.get('markup_rate', group_option.markup_rate))
                unit_cost = (gold_price * gold)  + sub_cost
                raw_price = unit_cost * markup_rate 
                # 천원 단위 반올림
                price = round(raw_price / 100) * 100
                if abs(price) > product.price * 0.5:
                    raise ValueError(f"옵션 가격이 상품의 가격의 50% 초과입니다!")
                group_option.gold = gold
                group_option.sub_cost = sub_cost
                group_option.markup_rate = markup_rate
                group_option.price = price
                group_option.save()
            product.option_group_flag=flag
            product.save()
    except ValueError as e:
        return JsonResponse({'message': str(e)}, status=400)
    except:
        return JsonResponse({'message': '업데이트 실패'}, status=400)
    return JsonResponse({'message': f'모든 옵션 상품 가격이 1돈 {int(gold_price*3.75):,.0f}원 가격으로 업데이트되었습니다!'}, status=200)

@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def fetch_option(request, *args, **kwargs):
    product_id = kwargs.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found.'}, status=400)
    access_token = get_valid_token()
    try:
        options = get_option_by_channel_product_no(access_token=access_token, channel_product_no=product.channel_product_no)
    except ValueError as e:
        return JsonResponse({'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'message': f'API 요청 에러: {e}'}, status=400)
    
    group_option_data = []  # 옵션 데이터를 위한 리스트
    for opt in options['options']:
        group_option_data.append({
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
            GroupOption.objects.filter(product=product).delete()
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
            product.option_group_name1 = options["option_group_name1"]
            product.option_group_name2 = options["option_group_name2"]
            product.option_group_name3 = options["option_group_name3"]
            product.option_group_quantity = options["option_group_quantity"]
            product.option_group_flag = False
            product.save()

    except Exception as e:
        return JsonResponse({'message': f'동기화 실패 : {e}'}, status=400)

    return JsonResponse({'message': '옵션 동기화 완료!'}, status=200)

