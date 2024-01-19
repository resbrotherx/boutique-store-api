from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from core.models import *

@receiver(post_save, sender=User)
def user_activity_signal(sender, instance, created, **kwargs):
    if created:
        activity = 'User created'
    else:
        activity = 'User updated'

    UserActivity.objects.create(user=instance, activity=activity)


@receiver(post_save, sender=CartOrderProducts)
def add_to_cart_signal(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(user=instance.user, activity=f'Added {instance.product} to cart')
