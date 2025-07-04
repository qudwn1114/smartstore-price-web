from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
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