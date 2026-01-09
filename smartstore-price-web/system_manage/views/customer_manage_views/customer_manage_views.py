from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q, F, ExpressionWrapper, DecimalField, IntegerField, Case, When, Value, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.core.validators import RegexValidator
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings

from system_manage.decorators import permission_required
from system_manage.views.system_manage_views.auth_views import validate_birth, validate_phone
from system_manage.models import Customer

class CustomerManageView(View):
    '''
        고객 관리 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        context['active_menu1'] = 'customer'
        search_keyword = request.GET.get('search_keyword', '').strip()
        context['search_keyword'] = search_keyword

        paginate_by = '20'
        page = request.GET.get('page', '1')

        order = request.GET.get('order', 'desc')
        sort = request.GET.get('sort', 'created_at')
        context['order'] = order
        context['sort'] = sort

        if order == 'desc':
            ordering = [f'-{sort}', 'id']
        else:
            ordering = [f'{sort}', 'id']

        query = Q(delete_flag=False)
        if search_keyword:
            search_q = Q(name__icontains=search_keyword)

            if search_keyword.isdigit():
                search_q |= Q(phone=int(search_keyword))
            query &= search_q

        queryset = Customer.objects.filter(query).annotate(
            avatar_number=Case(
                When(gender='MALE', then=Value(1)),
                When(gender='FEMALE', then=Value(2)),
                default=Value(3),
                output_field=IntegerField()
            ),
            order_count=Count('orders'),
        ).order_by(*ordering)

        paginator = Paginator(queryset, paginate_by)
        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage, InvalidPage):
            page = 1
            page_obj = paginator.page(page)

        pagelist = paginator.get_elided_page_range(page, on_each_side=3, on_ends=1)
        context['total_customer_count'] = paginator.count
        context['pagelist'] = pagelist
        context['page_obj'] = page_obj
        context['last_page_number'] = paginator.num_pages        

        return render(request, 'customer_manage/customer_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        name = request.POST['name'].strip()
        if name == '':
            return JsonResponse({'message': '이름을 입력해주세요.'}, status=400)
        phone = request.POST['phone'].strip()
        if phone:
            if not validate_phone(phone):
                return JsonResponse({'message': '전화번호 형식 오류'}, status=400)
        gender = request.POST['gender']
        if Customer.objects.filter(phone=phone).exists():
            return JsonResponse({'message': '이미 가입된 전화번호입니다.'}, status=400)
        if gender:
            if gender not in ['MALE', 'FEMALE']:
                return JsonResponse({'message': '성별 형식 오류'}, status=400)    
        else:
            gender = None
        birth = request.POST['birth']
        comment = request.POST.get('comment', '').strip()   
        if not validate_birth(birth):
            return JsonResponse({'message': '생년월일 형식 오류'}, status=400)
        try:
            Customer.objects.create(
                name=name,
                phone=phone,
                gender=gender,
                birth=birth,
                comment=comment
            )
        except:
            return JsonResponse({'message': '등록 오류'}, status=400)
        return JsonResponse({'message' : '등록 되었습니다.', 'url': reverse('system_manage:customer_manage')},  status = 201)
    
@require_http_methods(["POST"])    
@permission_required(raise_exception=True)
def edit_customer(request):
    customer_id = int(request.POST['customer_id'])
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'message': 'Customer not found.'}, status=400)
    name = request.POST['name'].strip()
    if name == '':
        return JsonResponse({'message': '이름을 입력해주세요.'}, status=400)
    phone = request.POST['phone'].strip()
    if phone:
        if not validate_phone(phone):
            return JsonResponse({'message': '전화번호 형식 오류'}, status=400)
    gender = request.POST['gender']
    if Customer.objects.filter(phone=phone).exclude(pk=customer_id).exists():
        return JsonResponse({'message': '이미 가입된 전화번호입니다.'}, status=400)
    if gender:
        if gender not in ['MALE', 'FEMALE']:
            return JsonResponse({'message': '성별 형식 오류'}, status=400)    
    else:
        gender = None
    birth = request.POST['birth']
    comment = request.POST.get('comment', '').strip()
    try:
        with transaction.atomic():
            customer.name = name
            customer.phone = phone  
            customer.gender = gender
            customer.birth = birth
            customer.comment = comment
            customer.save()
    except:
        return JsonResponse({'message': 'Error occurred while updating customer.'}, status=400)

    return JsonResponse({'message': '삭제 되었습니다.'}, status=200)

@require_http_methods(["POST"])    
@permission_required(raise_exception=True)
def delete_customer(request):
    customer_id = int(request.POST['customer_id'])
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'message': 'Customer not found.'}, status=400)
    try:
        with transaction.atomic():
            customer.delete_flag=True
            customer.phone = None
            customer.save()
    except:
        return JsonResponse({'message': 'Error occurred while deleting customer.'}, status=400)

    return JsonResponse({'message': '삭제 되었습니다.'}, status=200)