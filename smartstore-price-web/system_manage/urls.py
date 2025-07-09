from django.urls import path

from django.contrib.auth.views import LogoutView
from system_manage.views.system_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView, update_gold_price, update_naver_gold_price, GoldHistoryView
from system_manage.views.system_manage_views.user_views import UserDetailView
from system_manage.views.system_manage_views.product_views import create_product, edit_product, delete_product, bulk_update_product
from system_manage.views.system_manage_views.option_views import get_option, edit_option, fetch_option
from system_manage.views.system_manage_views.apply_views import create_apply_task, polling_apply_task, apply_product, bulk_apply_product

app_name='system_manage'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='system_manage:login'), name='logout'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),

    path('gold-price/', update_gold_price),
    path('gold-price/naver/', update_naver_gold_price),
    path('gold-history/', GoldHistoryView.as_view(), name='gold_history'),

    path('product/create/', create_product),
    path('product/edit/', edit_product),
    path('product/delete/', delete_product),
    path('product/bulk-update/', bulk_update_product),

    path('apply-task/create/', create_apply_task),
    path('apply-task/<int:apply_task_id>/polling/', polling_apply_task),
    path('product/apply/', apply_product),
    path('product/bulk-apply/', bulk_apply_product),

    path('product/<int:product_id>/option/', get_option),
    path('product/<int:product_id>/option/edit/', edit_option),
    path('product/<int:product_id>/option/fetch/', fetch_option),

    path('user-detail/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]