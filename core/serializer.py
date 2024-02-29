from .models import *
from userauths.models import *
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User as us

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ('id', 'username', 'email')
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# serializers.py
# serializers.py
class BrandSerializer(serializers.ModelSerializer):
    total_products = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = Brands
        fields = '__all__'
        
# class UserActivitySerializer(serializers.ModelSerializer):

#     class Meta:
#         model = UserActivity
#         fields = '__all__'

# class UsersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username']

class UserActivitySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserActivity
        fields = ['id', 'activity', 'timestamp','user']

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = wishlist_model
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        

# CartOrderSerializer
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'

# class UserActivitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserActivity
#         fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartOrder
        fields = '__all__'

class CartOrderProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartOrderProducts
        fields = '__all__'

# class CartOrderProductsSerializer(serializers.ModelSerializer):
#     user = serializers.SerializerMethodField()

#     class Meta:
#         model = CartOrderProducts
#         fields = ['id', 'order', 'invoice_no', 'product_status', 'item', 'image', 'qty', 'price', 'total', 'user']

    # def get_user(self, instance):
    #     return instance.order.user.id if instance.order.user else None


class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    qty = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    # image = serializers.ImageField()
    image = serializers.CharField()
    pid = serializers.CharField()



class ProductReviewFormSerializer(serializers.ModelSerializer):
    # Assuming 'review' and 'rating' are the field names in your ProductReviewForm
    review = serializers.CharField(required=False)
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = ProductReview
        fields = ['review', 'rating']





        