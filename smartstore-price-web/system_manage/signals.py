from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from system_manage.models import Customer, Order
from system_manage.services.customer_cache import clear_customer_cache, clear_order_status_cache


@receiver(post_save, sender=Customer)
def customer_post_save(sender, **kwargs):
    clear_customer_cache()


@receiver(post_delete, sender=Customer)
def customer_post_delete(sender, **kwargs):
    clear_customer_cache()


@receiver(post_save, sender=Order)
def clear_order_status_cache_on_save(sender, instance, **kwargs):
    clear_order_status_cache()

@receiver(post_delete, sender=Order)
def clear_order_status_cache_on_delete(sender, instance, **kwargs):
    clear_order_status_cache()