from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    birth = models.DateField(null=True, verbose_name='생년월일', default='2000-01-01')
    membername = models.CharField(default='', max_length=50, verbose_name='회원명')
    gender = models.CharField(null=True, max_length=10, verbose_name='성별', choices=(('MALE', '남성'), ('FEMALE', '여성')))

    class Meta:
        db_table='auth_profile'
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Token(models.Model):
    access_token = models.CharField(max_length=400)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table='token'

class CrawlTarget(models.Model):
    name = models.CharField(max_length=100, verbose_name='크롤링 대상 이름')
    url = models.URLField(max_length=500, verbose_name='크롤링 대상 URL')
    xpath = models.CharField(max_length=500, verbose_name='크롤링 대상 XPath')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table='crawl_target'

class GoldPrice(models.Model):
    price = models.PositiveIntegerField(verbose_name='금 가격')
    naver_price = models.PositiveIntegerField(verbose_name='네이버 금 가격')
    updated_at = models.DateTimeField(verbose_name='수정일')
    naver_updated_at = models.DateTimeField(verbose_name='네이버 수정일')

    class Meta:
        db_table='gold_price'


class GoldPriceHistory(models.Model):
    price = models.PositiveIntegerField(verbose_name='금 가격')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table='gold_price_history'


class Product(models.Model):
    origin_product_no = models.BigIntegerField(verbose_name='원 상품 번호', unique=True)
    channel_product_no = models.BigIntegerField(verbose_name='채널 상품 번호', unique=True)
    name = models.CharField(max_length=255, verbose_name='상품명')
    gold = models.DecimalField(max_digits=10, decimal_places=5, verbose_name='중량')
    labor_cost = models.PositiveIntegerField(verbose_name='공임비')
    sub_cost = models.PositiveIntegerField(verbose_name='부가비용')
    markup_rate = models.DecimalField(max_digits=10, decimal_places=5, verbose_name='판매가 배율')
    price = models.PositiveIntegerField(verbose_name='판매가')
    option_group_quantity = models.PositiveIntegerField(verbose_name='옵션 그룹 수량', default=0)
    option_group_name1 = models.CharField(max_length=255, verbose_name='옵션 그룹명1', null=True)
    option_group_name2 = models.CharField(max_length=255, verbose_name='옵션 그룹명2', null=True)
    option_group_name3 = models.CharField(max_length=255, verbose_name='옵션 그룹명3', null=True)
    option_group_flag = models.BooleanField(default=False, verbose_name='옵션 그룹 업데이트 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table='product'

class GroupOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    option_id = models.BigIntegerField(verbose_name='옵션 ID', unique=True)
    option_name1 = models.CharField(max_length=255, verbose_name='옵션명1', null=True)
    option_name2 = models.CharField(max_length=255, verbose_name='옵션명2', null=True)
    option_name3 = models.CharField(max_length=255, verbose_name='옵션명3', null=True)
    gold = models.DecimalField(max_digits=10, decimal_places=5, verbose_name='중량')
    sub_cost = models.IntegerField(verbose_name='부가비용')
    markup_rate = models.DecimalField(max_digits=10, decimal_places=5, verbose_name='판매가 배율')
    price = models.IntegerField(verbose_name='판매가')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table='group_option'

class ApplyTaskHistory(models.Model):
    progress = models.PositiveSmallIntegerField(default=0)
    status = models.BooleanField(default=False)
    status_message = models.CharField(max_length=255, default="작업 준비 중 입니다.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table='apply_task_history'