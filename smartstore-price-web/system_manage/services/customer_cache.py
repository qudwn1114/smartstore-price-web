from django.core.cache import cache
from django.db.models import Count, Q
from system_manage.models import Customer, Order


CUSTOMER_LIST_CACHE_KEY = 'customers:list:v1'
CUSTOMER_LIST_CACHE_TTL = 60 * 10  # 10분

ORDER_STATUS_COUNT_CACHE_KEY = 'order_status_count:v1'
ORDER_STATUS_COUNT_CACHE_TTL = 60 * 10  # 10분

def get_cached_customers():
    """
        삭제되지 않은 고객 목록 캐싱 조회
    """
    customers = cache.get(CUSTOMER_LIST_CACHE_KEY)
    if customers is not None:
        return customers
    customers = list(
        Customer.objects
        .filter(delete_flag=False)
        .order_by('name')
        .values('id', 'name', 'phone')
    )

    cache.set(CUSTOMER_LIST_CACHE_KEY, customers, CUSTOMER_LIST_CACHE_TTL)
    return customers


def clear_customer_cache():
    cache.delete(CUSTOMER_LIST_CACHE_KEY)


def get_cached_order_status_count():
    """
        전체 주문 상태별 count 반환
    """
    # 캐시 확인
    order_status_count_dict = cache.get(ORDER_STATUS_COUNT_CACHE_KEY)
    if order_status_count_dict:
        return order_status_count_dict

    # 캐시 없으면 DB에서 aggregate
    status_count = Order.objects.aggregate(
        status_0=Count('id', filter=Q(status=0)),
        status_1=Count('id', filter=Q(status=1)),
        status_2=Count('id', filter=Q(status=2)),
        status_3=Count('id', filter=Q(status=3)),
    )
    order_status_count_dict = {
        '0': status_count['status_0'],
        '1': status_count['status_1'],
        '2': status_count['status_2'],
        '3': status_count['status_3'],
    }
    cache.set('order_status_count', order_status_count_dict, ORDER_STATUS_COUNT_CACHE_TTL)
    return order_status_count_dict

def clear_order_status_cache():
    cache.delete(ORDER_STATUS_COUNT_CACHE_KEY)