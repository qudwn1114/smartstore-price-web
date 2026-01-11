from django.shortcuts import render, redirect, get_object_or_404
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
from system_manage.models import Customer, Order

class OrderManageView(View):
    '''
        주문 관리 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        context['active_menu1'] = 'order'
        search_keyword = request.GET.get('search_keyword', '').strip()
        context['search_keyword'] = search_keyword

        paginate_by = '20'
        page = request.GET.get('page', '1')

        order = request.GET.get('order', 'desc')
        sort = request.GET.get('sort', 'created_at')
        context['order'] = order
        context['sort'] = sort

        context['customers'] = Customer.objects.filter(delete_flag=False).values('id', 'name', 'phone')

        if order == 'desc':
            ordering = [f'-{sort}', '-id']
        else:
            ordering = [f'{sort}', 'id']

        query = Q()
        if search_keyword:
            search_q = Q(customer__name__icontains=search_keyword)
            if search_keyword.isdigit():

                search_q |= Q(customer__phone=search_keyword)
            query &= search_q

        queryset = Order.objects.filter(query).annotate(
            avatar_number=Case(
                When(customer__gender='MALE', then=Value(1)),
                When(customer__gender='FEMALE', then=Value(2)),
                default=Value(3),
                output_field=IntegerField()
            ),
        ).order_by(*ordering)

        paginator = Paginator(queryset, paginate_by)
        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage, InvalidPage):
            page = 1
            page_obj = paginator.page(page)

        pagelist = paginator.get_elided_page_range(page, on_each_side=3, on_ends=1)
        context['total_count'] = paginator.count
        context['pagelist'] = pagelist
        context['page_obj'] = page_obj
        context['last_page_number'] = paginator.num_pages        

        return render(request, 'customer_manage/order_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        order_name = request.POST['order_name'].strip()
        if order_name == '':
            return JsonResponse({'message': '주문명을 입력해주세요.'}, status=400)
        order_date = request.POST['order_date']
        if not validate_birth(order_date):
            return JsonResponse({'message': '주문날짜 형식 오류'}, status=400)
        total_price = int(request.POST['total_price'])
        status = request.POST['status']
        customer_id = request.POST.get('customer_id')
        if status not in ['0', '1', '2', '3']:
            return JsonResponse({'message': '상태 형식 오류'}, status=400)
        if customer_id:
            try:
                customer = Customer.objects.get(id=int(customer_id))
            except Customer.DoesNotExist:
                return JsonResponse({'message': '찾을 수 없는 고객입니다.'}, status=400)
        else:
            customer = None

        comment = request.POST.get('comment', '').strip()   
        
        try:
            Order.objects.create(
                order_name = order_name,
                order_date = order_date,
                total_price = total_price,
                status = status,
                customer = customer,
                comment = comment
            )
        except:
            return JsonResponse({'message': '등록 오류'}, status=400)
        return JsonResponse({'message' : '등록 되었습니다.', 'url': reverse('system_manage:order_manage')},  status = 201)
    
@require_http_methods(["POST"])    
@permission_required(raise_exception=True)
def edit_order(request):
    order_id = int(request.POST['order_id'])
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'message': 'Order not found.'}, status=400)
    order_name = request.POST['order_name'].strip()
    if order_name == '':
        return JsonResponse({'message': '주문명을 입력해주세요.'}, status=400)
    order_date = request.POST['order_date']
    if not validate_birth(order_date):
        return JsonResponse({'message': '주문날짜 형식 오류'}, status=400)
    total_price = int(request.POST['total_price'])
    status = request.POST['status']
    customer_id = request.POST.get('customer_id')
    if status not in ['0', '1', '2', '3']:
        return JsonResponse({'message': '상태 형식 오류'}, status=400)
    if customer_id:
        try:
            customer = Customer.objects.get(id=int(customer_id))
        except Customer.DoesNotExist:
            return JsonResponse({'message': '찾을 수 없는 고객입니다.'}, status=400)
    else:
        customer = None

    comment = request.POST.get('comment', '').strip()   
    try:
        with transaction.atomic():
            order.order_name = order_name
            order.order_date = order_date
            order.total_price = total_price
            order.status =status
            order.comment = comment
            order.customer = customer
            order.save()
    except:
        return JsonResponse({'message': 'Error occurred while updating order.'}, status=400)

    return JsonResponse({'message': '수정 되었습니다.'}, status=200)

@require_http_methods(["POST"])    
@permission_required(raise_exception=True)
def delete_order(request):
    order_id = int(request.POST['order_id'])
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'message': 'Order not found.'}, status=400)
    try:
        order.delete()
    except:
        return JsonResponse({'message': 'Error occurred while deleting order.'}, status=400)

    return JsonResponse({'message': '삭제 되었습니다.'}, status=200)


@require_http_methods(["POST"])    
@permission_required(raise_exception=True)
def order_status(request):
    order_id = int(request.POST['order_id'])
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'message': 'Order not found.'}, status=400)
    status = request.POST['status']
    if status not in ['0', '1', '2', '3']:
        return JsonResponse({'message': '상태 형식 오류'}, status=400)
    try:
        with transaction.atomic():
            order.status =status
            order.save()
    except:
        return JsonResponse({'message': 'Error occurred while updating order.'}, status=400)

    return JsonResponse({'message': '업데이트 되었습니다.'}, status=200)



class CustomerOrderManageView(View):
    '''
        주문 관리 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        customer_id = kwargs.get('customer_id')
        customer = get_object_or_404(Customer, pk=customer_id)
        context['customer'] = customer
        
        context['active_menu1'] = 'order'
        search_keyword = request.GET.get('search_keyword', '').strip()
        context['search_keyword'] = search_keyword

        paginate_by = '20'
        page = request.GET.get('page', '1')

        order = request.GET.get('order', 'desc')
        sort = request.GET.get('sort', 'created_at')
        context['order'] = order
        context['sort'] = sort

        if order == 'desc':
            ordering = [f'-{sort}', '-id']
        else:
            ordering = [f'{sort}', 'id']

        context['customers'] = Customer.objects.filter(delete_flag=False).values('id', 'name', 'phone')

        query = Q(customer=customer)

        queryset = Order.objects.filter(query).annotate(
            avatar_number=Case(
                When(customer__gender='MALE', then=Value(1)),
                When(customer__gender='FEMALE', then=Value(2)),
                default=Value(3),
                output_field=IntegerField()
            ),
        ).order_by(*ordering)

        paginator = Paginator(queryset, paginate_by)
        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage, InvalidPage):
            page = 1
            page_obj = paginator.page(page)

        pagelist = paginator.get_elided_page_range(page, on_each_side=3, on_ends=1)
        context['total_count'] = paginator.count
        context['pagelist'] = pagelist
        context['page_obj'] = page_obj
        context['last_page_number'] = paginator.num_pages        

        return render(request, 'customer_manage/customer_order_manage.html', context)