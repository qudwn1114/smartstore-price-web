from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import View, TemplateView
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q, F, ExpressionWrapper, DecimalField
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.core.validators import RegexValidator
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings

from system_manage.decorators import permission_required
from system_manage.naver_commerce import get_valid_token, get_product_by_channel_product_no, get_option_by_channel_product_no
from system_manage.models import GoldPrice, GoldPriceHistory, CrawlTarget, Product, GroupOption

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from decimal import Decimal
import datetime, json, requests, os, time, platform, logging, traceback

# Create your views here.
class HomeView(TemplateView):
    '''
        관리자 메인 화면
    '''
    template_name = 'system_manage/admin_main.html'
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        context['active_menu1'] = 'dashboard'
        gold_price, created = GoldPrice.objects.get_or_create(
            id=1,  # Assuming there's only one record for gold price
            defaults={
                'price': 0,
                'naver_price': 0,
                'updated_at': timezone.now(),
                'naver_updated_at': timezone.now()
            }
        )
        context['gold_price'] = {
            'price': gold_price.price,
            'don_price': int(gold_price.price * 3.75),  
            'naver_price': gold_price.naver_price,
            'don_naver_price': int(gold_price.naver_price * 3.75),
            'updated_at': gold_price.updated_at,
            'naver_updated_at': gold_price.naver_updated_at
        }
        search_keyword = request.GET.get('search_keyword', '').strip()
        context['search_keyword'] = search_keyword
        query = Q()
        if search_keyword:
            query |= Q(name__icontains=search_keyword)  # 항상 name 검색 포함
            if search_keyword.isdigit():
                search_number = int(search_keyword)
                query |= Q(channel_product_no=search_number)
                query |= Q(origin_product_no=search_number)  # 원상품 번호도 숫자일 경우 포함

        product_list = Product.objects.annotate(
            gold_don=ExpressionWrapper(
                F('gold') / 3.75,
                output_field=DecimalField(max_digits=10, decimal_places=5)
            )
        ).filter(query).values(
            'id', 'origin_product_no', 'channel_product_no', 'name', 'gold',
            'labor_cost', 'sub_cost', 'markup_rate', 'price',
            'option_group_quantity', 'option_group_flag', 'option_group_name1', 'option_group_name2', 'option_group_name3', 'gold_don').order_by('-created_at')

        context['product_list'] = product_list
        context['total_product_count'] = product_list.count()

        return render(request, self.template_name, context)

@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def update_gold_price(request):
    try:
        price = int(request.POST['price'])
        new_price = int(price/3.75)
        with transaction.atomic():
            try:
                gold_price = GoldPrice.objects.get(id=1)
            except GoldPrice.DoesNotExist:
                return JsonResponse({'message': 'Gold price not found.'}, status=404)
            if gold_price.price == new_price:
                return JsonResponse({'message': '이전 시세와 동일 합니다.'}, status=400)
            gold_price.price = new_price
            gold_price.updated_at = timezone.now()
            gold_price.save()
            GoldPriceHistory.objects.create(
                price=new_price
            )
        return JsonResponse({'message': '시세가 업데이트 되었습니다.'}, status=200)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
    
@require_http_methods(["POST"])
@permission_required(raise_exception=True)
def update_naver_gold_price(request):
    crawl_target, created = CrawlTarget.objects.get_or_create(
        id=1,  # Assuming there's only one record for gold price
        defaults={
            'url': 'https://m.stock.naver.com/marketindex/home/metals',
            'xpath': '//*[@id="content"]/div[2]/ul/li[2]/a/span[1]'
        }
    )
    url = crawl_target.url
    xpath = crawl_target.xpath
    if not url or not xpath:
        return JsonResponse({'message': 'Crawl target not set.'}, status=400)
    try:
        gold_price = GoldPrice.objects.get(id=1)
    except GoldPrice.DoesNotExist:
        return JsonResponse({'message': 'Gold price not found.'}, status=404)
    try:
        # 네이버 금 시세 URL
        # 웹 페이지 요청
        response = requests.get(url)
        if response.status_code == 200:
            # 운영 체제 확인
            system_os = platform.system()
            # Selenium 웹드라이버 설정 133.0.....
            if system_os == 'Windows':
                chrome_driver_path = os.path.join(settings.BASE_DIR, 'chrome_drivers/windows', 'chromedriver.exe')
            elif system_os == 'Darwin':  # macOS
                chrome_driver_path = os.path.join(settings.BASE_DIR, 'chrome_drivers/mac', 'chromedriver')
            elif system_os == 'Linux':  # Linux
                chrome_driver_path = os.path.join(settings.BASE_DIR, 'chrome_drivers/linux', 'chromedriver')
            else:
                raise Exception(f"Unsupported OS: {system_os}")

            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 헤드리스 모드 (브라우저 UI 없이 실행)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # 이미지 로딩 비활성화
            service = Service(chrome_driver_path)  # chromedriver 경로 설정
            # 웹드라이버 실행
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            # 페이지 로드 대기 (동적 콘텐츠 로딩을 위한 대기)
            time.sleep(2)
            # XPath를 사용하여 금 가격 찾기
            try:
                gold_price_tag = driver.find_element(By.XPATH, xpath)
                gold_price_text = gold_price_tag.text
                print(f"현재 금 가격: {gold_price_text}")
            except Exception as e:
                driver.quit()
                return JsonResponse({'message': '크롤링 오류 금 시세를 불러오는데 실패했습니다.'}, status=400)
            # 드라이버 종료
            driver.quit()
            naver_gold_price = int(gold_price_text.replace(",", "").strip())
            gold_price.naver_price = naver_gold_price
            gold_price.naver_updated_at = timezone.now()
            gold_price.save()
    except Exception:
        logger = logging.getLogger('my')
        logger.error(traceback.format_exc())
        return JsonResponse({'message': '네이버 금 시세를 불러오는데 실패했습니다.'}, status=400)
    return JsonResponse({'message': '네이버 금 시세가 업데이트 되었습니다.'}, status=200)

class LoginView(View):
    '''
        관리자 로그인 기능
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        if request.user.is_authenticated:
            return redirect('system_manage:home')
                
        return render(request, 'system_manage/admin_login.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            return JsonResponse({'message':'Incorrect username'}, status = 400)
        
        if not user.check_password(raw_password=password):
            return JsonResponse({'message':'Incorrect password.'}, status = 400)
        if not user.is_active:
            return JsonResponse({'message':'Deactivated account.'}, status = 400)
        
        if user.is_superuser:
            login(request, user)
            if 'next' in request.GET:
                url = request.GET.get('next')
                url = url.split('?next=')[-1]
            else:
                url = reverse('system_manage:home')
            get_valid_token()
            return JsonResponse({'message':'Sign in completed.', 'url':url}, status = 200)
        else:
            return JsonResponse({'message':'Not an administrator.'}, status = 403)

class PermissionDeniedView(LoginRequiredMixin, TemplateView):
    login_url = 'system_manage:login'
    template_name='system_manage/permission_denied.html'


class NotFoundView(LoginRequiredMixin, TemplateView):
    login_url = 'system_manage:login'
    template_name='system_manage/not_found.html'

def validate_username(username):
    '''
        아이디 유효성 체크
    '''
    try:
        RegexValidator(regex=r'^[a-z0-9]{6,20}$')(username)
    except:
        return False

    return True

def validate_password(password):
    '''
        비밀번호 유효성 체크
    '''
    try:
        # Minimum eight characters Maximum 16 characters, at least one letter and one number
        RegexValidator(regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_\-+={}\[\]:;"\'<>,.?/~`|\\]{8,16}$')(password)
    except:
        return False

    return True


def validate_birth(birth):
    '''
    생년월일 유효성체크
    '''
    try:
        birth = datetime.datetime.strptime(birth, "%Y-%m-%d")
    except ValueError:
        return False
    
    return True

def validate_phone(phone):
    '''
        전화번호 유효성 체크
    '''
    try:
        RegexValidator(regex=r'^01([0-9]{1})([0-9]{4})([0-9]{4})$')(phone)
    except:
        return False

    return True


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
    