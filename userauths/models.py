from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser

SEX = (
    ("male", "Male"),
    ("female", "Female"),
    ("none", "None"),
)
ROLE = (
    ("director", "Director"),
    ("seles_manager", "Sales Manager"),
    ("sales_supervisor", "Sales Supervisor"),
    ("sales_advisor", "Sales Advisor"),
    ("developer", "Developer"),
    ("customer", "Customer"),
)
COLOR = (
    ("red", "Red"),
    ("green", "Green"),
    ("blue", "Blue"),
    ("black", "Black"),
)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    # bio = models.CharField(max_length=100)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


    def profile(self):
        profile = Profile.objects.get(user=self)

    # def __str__(self):
    #     return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=1000, default='none')
    full_name = models.CharField(max_length=1000)
    bio = models.CharField(max_length=100)
    role = models.CharField(
        choices=ROLE, max_length=30, default="customer")
    color = models.CharField(
        choices=COLOR, max_length=30, default="blue")
    phone = models.CharField(max_length=200, default='+000 000000') # +234 (456) - 789
    sex = models.CharField(
        choices=SEX, max_length=30, default="none")
    image = models.ImageField(upload_to="user_images", default="default.jpg")
    verified = models.BooleanField(default=False)


class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200) # +234 (456) - 789
    subject = models.CharField(max_length=200) # +234 (456) - 789
    message = models.TextField()

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)