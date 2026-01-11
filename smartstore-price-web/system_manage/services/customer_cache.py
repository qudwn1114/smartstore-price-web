from django.core.cache import cache
from system_manage.models import Customer

CUSTOMER_LIST_CACHE_KEY = 'customers:list:v1'
CUSTOMER_LIST_CACHE_TTL = 60 * 10  # 10분

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
        .values('id', 'name', 'phone')
    )

    cache.set(CUSTOMER_LIST_CACHE_KEY, customers, CUSTOMER_LIST_CACHE_TTL)
    return customers


def clear_customer_cache():
    cache.delete(CUSTOMER_LIST_CACHE_KEY)