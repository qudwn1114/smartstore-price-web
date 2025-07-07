from django.urls import path

from django.contrib.auth.views import LogoutView
from system_manage.views.system_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView, update_gold_price, update_naver_gold_price,\
    create_product, edit_product, delete_product, get_option, edit_option, fetch_option
from system_manage.views.system_manage_views.summernote_views import summernote_image_upload_view
app_name='system_manage'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='system_manage:login'), name='logout'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),

    path('gold-price/', update_gold_price),
    path('gold-price/naver/', update_naver_gold_price),

    path('product/create/', create_product),
    path('product/edit/', edit_product),
    path('product/delete/', delete_product),

    path('product/<int:product_id>/option/', get_option),
    path('product/<int:product_id>/option/edit/', edit_option),
    path('product/<int:product_id>/option/fetch/', fetch_option),

    path('summernote/upload-image/', summernote_image_upload_view),
]