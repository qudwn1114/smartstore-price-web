from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import View, TemplateView
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.core.validators import RegexValidator
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings

from system_manage.decorators import permission_required
from system_manage.naver_commerce import get_valid_token
from system_manage.models import GoldPrice, GoldPriceHistory, CrawlTarget

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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