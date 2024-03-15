
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from requests import session
from taggit.models import Tag
from core.models import *
from userauths.models import ContactUs, Profile
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
from rest_framework.exceptions import ValidationError
import requests
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
import calendar
from django.db.models import Count, Avg
from django.db.models.functions import ExtractMonth
from django.core import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.renderers import JSONRenderer
from .serializer import *
from rest_framework.authentication import TokenAuthentication
import secrets
import json
from django.db import transaction
import random
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.models import User
from userauths.models import User


def generate_otp():
	return str(random.randint(100000, 999999))

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def index(request):
	if request.method == 'GET':
		prod= Product.objects.filter(product_status="published", featured=True).order_by("-id")
		products = ProductSerializer(prod, many=True)
		context = {
			"products":products.data
		}
		# data = f"Congratulation {request.user}, your API just responded to GET request"
		return Response(context, status=status.HTTP_200_OK)
	return Response({}, status.HTTP_400_BAD_REQUEST)
	


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def slider(request):
	if request.method == 'GET':
		prod= Slider.objects.all().order_by("-id")
		slide = SliderSerializer(prod, many=True)
		context = {
			"slider":slide.data
		}
		return Response(context, status=status.HTTP_200_OK)
	return Response({}, status.HTTP_400_BAD_REQUEST)
	

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def product_list_view(request):
	try:
		if request.method == 'GET':
			prod = Product.objects.filter(product_status="published").order_by("-id")
			products = ProductSerializer(prod, many=True)
			# tags = Tag.objects.all().order_by("-id")[:6]
			context = {
				"products":products.data,
				# "tags":tags,
			}
			return Response(context, status=status.HTTP_200_OK)
	except Product.DoesNotExist:
		return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
	return Response({}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_detail_view(request, pid):
	try:
		product = Product.objects.get(pid=pid)
		products = Product.objects.filter(category=product.category).exclude(pid=pid)
		# Getting all reviews related to a product
		reviews = ProductReview.objects.filter(product=product).order_by("-date")
		# Getting average review
		average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
		# Product Review form
		review_form = ProductReviewForm()
		review_form_data = ProductReviewFormSerializer(review_form).data
		make_review = True

		try:
			address = Address.objects.get(status=True, user=request.user)
		except Address.DoesNotExist:
			address = "Default Address"  # Provide a default address or handle it as needed

		user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

		if user_review_count > 0:
			make_review = False

		p_image = product.p_images.all()

		# Serialize data
		product_data = ProductSerializer(product).data
		products_data = ProductSerializer(products, many=True).data
		reviews_data = ProductReviewSerializer(reviews, many=True).data

		context = {
			"products": product_data,
			"address": address,
			"make_review": make_review,
			"review_form": review_form_data,
			"p_image": p_image,
			"average_rating": average_rating,
			"reviews": reviews_data,
			"similar_product": products_data,
		}

		return Response(context, status=status.HTTP_200_OK)

	except Product.DoesNotExist:
		return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def dashboard_all_product_view(request):
	try:
		if request.method == 'GET':
			prod = Product.objects.all().order_by("-id")
			products = ProductSerializer(prod, many=True)
			# tags = Tag.objects.all().order_by("-id")[:6]
			context = {
				"products":products.data,
				# "tags":tags,
			}
			return Response(context, status=status.HTTP_200_OK)
		# elif request.method == "POST":

	except Product.DoesNotExist:
		return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
	return Response({}, status.HTTP_400_BAD_REQUEST)
	 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_list_view(request):
	try:
		if request.method == 'GET':
			cate = Category.objects.all()
			categories = CategorySerializer(cate, many=True)
			context = {
				"products":categories.data
			}
			return Response(context, status=status.HTTP_200_OK)
	except Category.DoesNotExist:
		return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
	return Response({}, status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_product_list__view(request, cid):
	try:
		if request.method == 'GET':
			category = Category.objects.get(cid=cid)  # Replace 'cid' with the actual field name in your Category model
			products = Product.objects.filter(product_status="published", category=category)
			serializer = ProductSerializer(products, many=True)
			category_serializer = CategorySerializer(category)
			context = {
				"category": category_serializer.data,
				"products": serializer.data,
			}
			return Response(context, status=status.HTTP_200_OK)
	except Category.DoesNotExist:
		return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subcategory_list_view(request, cid):
	try:
		if request.method == 'GET':
			category = Category.objects.get(cid=cid)
			subcategories = SubCategory.objects.filter(category=category)
			serializer = SubCategorySerializer(subcategories, many=True)
			category_serializer = CategorySerializer(category)
			context = {
				"category": category_serializer.data,
				"subcategories": serializer.data,
			}
			return Response(context, status=status.HTTP_200_OK)
	except Category.DoesNotExist:
		return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
	except SubCategory.DoesNotExist:
		return Response({"error": "Subcategories not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# views.py
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def brands_list_view(request):
	if request.method == 'GET':
		try:
			brands = Brands.objects.annotate(total_products=Count('product'))
			brand_serialized = BrandSerializer(brands, many=True)
			context = {"brands": brand_serialized.data}
			return Response(context, status=status.HTTP_200_OK)
		except Brands.DoesNotExist:
			return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
	elif request.method == 'POST':
		try:
			data = request.data
			serializer = BrandSerializer(data={'user': request.user.id, 'title': data['title']})
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brand_detail_view(request, vid):
	if request.method == 'GET':
		try:
			brand_instance = Brands.objects.get(vid=vid)
			brand_serializer = BrandSerializer(brand_instance)
			context = {
				"brand": brand_serializer.data,
			}
			return Response(context, status=status.HTTP_200_OK)
		except Brands.DoesNotExist:
			return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
	return Response({}, status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category_and_subcategories(request):
    try:
        if request.method == 'POST':
            data = request.data
            category_data = data.get('category')
            subcategories_data = data.get('subcategories')

            # Check if the category already exists
            existing_category = Category.objects.filter(title=category_data.get('title')).first()
            if existing_category:
                return Response({"error": "Category already exists"}, status=status.HTTP_400_BAD_REQUEST)

            # Create the category
            category_serializer = CategorySerializer(data=category_data)
            if category_serializer.is_valid():
                category = category_serializer.save()
            else:
                return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Save subcategories
            if isinstance(subcategories_data, list):
                for subcategory_data in subcategories_data:
                    save_subcategory(category, subcategory_data)
            elif isinstance(subcategories_data, dict):
                save_subcategory(category, subcategories_data)
            else:
                return Response({"error": "Invalid subcategories data format"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Category with subcategories created successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def save_subcategory(category, subcategory_data):
    existing_subcategory = SubCategory.objects.filter(title=subcategory_data.get('title')).first()
    if existing_subcategory:
        raise ValueError(f"Subcategory '{subcategory_data.get('title')}' already exists")

    subcategory_data['category'] = category.pk
    subcategory_serializer = SubCategorySerializer(data=subcategory_data)
    if subcategory_serializer.is_valid():
        subcategory_serializer.save()
    else:
        raise ValueError(subcategory_serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def all_product_list(request):
	try:
		if request.method == 'GET':
			prod = Product.objects.all().order_by("-id")
			products = ProductSerializer(prod, many=True)
			# tags = Tag.objects.all().order_by("-id")[:6]
			context = {
				"products":products.data,
				# "tags":tags,
			}
			return Response(context, status=status.HTTP_200_OK)
	except Product.DoesNotExist:
		return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
	return Response({}, status.HTTP_400_BAD_REQUEST)
	 

# def product_detail_view(request, pid):
#   if request.method == 'GET':
#     product = Product.objects.get(pid=pid)
#     # product = get_object_or_404(Product, pid=pid)
#     products = Product.objects.filter(category=product.category).exclude(pid=pid)

#     # Getting all reviews related to a product
#     reviews = ProductReview.objects.filter(product=product).order_by("-date")

#     # Getting average review
#     average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

#     # Product Review form
#     review_form = ProductReviewForm()


#     make_review = True 

#     if request.user.is_authenticated:
#       address = Address.objects.get(status=True, user=request.user)
#       user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

#       if user_review_count > 0:
#         make_review = False
		
#     address = "Login To Continue"


#     p_image = product.p_images.all()

#     context = {
#       "p": product,
#       "address": address,
#       "make_review": make_review,
#       "review_form": review_form,
#       "p_image": p_image,
#       "average_rating": average_rating,
#       "reviews": reviews,
#       "products": products,
#     }

#     return Response(context, status=status.HTTP_200_OK)
#   return Response({}, status.HTTP_400_BAD_REQUEST)





@api_view(['GET','POST'])
def tag_list(request, tag_slug=None):
	if request.method == 'GET':
		products = Product.objects.filter(product_status="published").order_by("-id")
		tag = None 
		if tag_slug:
			tag = get_object_or_404(Tag, slug=tag_slug)
			products = products.filter(tags__in=[tag])

		context = {
			"products": products,
			"tag": tag
		}
		return Response(context, status=status.HTTP_200_OK)
	elif request.method == 'POST':
		text = "Hello buddy"
		data = f'Congratulation your API just responded to POST request with text: {text}'
		return Response({'response': data}, status=status.HTTP_200_OK)
	return Response({}, status.HTTP_400_BAD_REQUEST)

	


def ajax_add_review(request, pid):
	product = Product.objects.get(pk=pid)
	user = request.user 

	review = ProductReview.objects.create(
		user=user,
		product=product,
		review = request.POST['review'],
		rating = request.POST['rating'],
	)

	context = {
		'user': user.username,
		'review': request.POST['review'],
		'rating': request.POST['rating'],
	}

	average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

	return JsonResponse(
		 {
		 'bool': True,
		'context': context,
		'average_reviews': average_reviews
		 }
	)

@api_view(['GET','POST'])
def search_view(request):
	if request.method == 'GET':
		query = request.GET.get("q")
		products = Product.objects.filter(title__icontains=query).order_by("-date")

		context = {
			"products": products,
			"query": query,
		}
		return Response(context, status=status.HTTP_200_OK)
	elif request.method == 'POST':
		text = "Hello buddy"
		data = f'Congratulation your API just responded to POST request with text: {text}'
		return Response({'response': data}, status=status.HTTP_200_OK)
	return Response({}, status.HTTP_400_BAD_REQUEST)
	

# @api_view(['GET'])
# @permission_classes([IsAuthenticated]) 
# def filter_product(request):
#   categories = request.GET.getlist("category[]")
#   brands = request.GET.getlist("brand[]")


#   min_price = request.GET['min_price']
#   max_price = request.GET['max_price']

#   products = Product.objects.filter(product_status="published").order_by("-id").distinct()

#   products = products.filter(price__gte=min_price)
#   products = products.filter(price__lte=max_price)


#   if len(categories) > 0:
#     products = products.filter(category__id__in=categories).distinct() 
#   else:
#     products = Product.objects.filter(product_status="published").order_by("-id").distinct()
#   if len(brands) > 0:
#     products = products.filter(brand__id__in=brands).distinct() 
#   else:
#     products = Product.objects.filter(product_status="published").order_by("-id").distinct()    
	
		 

	
#   data = render_to_string("core/async/product-list.html", {"products": products})
#   return JsonResponse({"data": data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_product(request, min_price, max_price, subCats, *args, **kwargs):
		try:
				# categories = request.GET.getlist("category[]")
				categories = subCats
				brands = request.GET.getlist("brand[]")

				products = Product.objects.filter(product_status="published").order_by("-id").distinct()
				products = products.filter(price__gte=min_price)
				products = products.filter(price__lte=max_price)

				if len(categories) > 0:
						products = products.filter(category__id__in=categories).distinct()
				if len(brands) > 0:
						products = products.filter(brand__id__in=brands).distinct()

				serializer = ProductSerializer(products, many=True)
				data = serializer.data

				# Optionally, you can render the data to HTML if needed
				# data_html = render_to_string("core/async/product-list.html", {"products": serializer.data})

				return Response({"products": data})
		except Exception as e:
				return Response({"error": str(e)}, status=500)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
	try:
		if request.method == 'GET':
			cart_product = {
				'id': int(request.GET['id']),
				'title': request.GET['title'],
				'qty': int(request.GET['qty']),
				'price': float(request.GET['price']),
				'image': request.GET['image'],
				'pid': request.GET['pid'],
			}

			if 'cart_data_obj' in request.session:
				cart_data = request.session['cart_data_obj']

				if str(cart_product['id']) in cart_data:
					cart_data[str(cart_product['id'])]['qty'] = cart_product['qty']
				else:
					cart_data.update({str(cart_product['id']): cart_product})
			else:
				cart_data = {str(cart_product['id']): cart_product}

			request.session['cart_data_obj'] = cart_data

			# Serialize the cart_data.values() as a list
			serializer = CartItemSerializer(data=list(cart_data.values()), many=True)
			serializer.is_valid(raise_exception=True)

			return JsonResponse({"data": serializer.data, 'totalcartitems': len(cart_data)})
	except KeyError as e:
		return Response({"error": f"Missing parameter: {str(e)}"}, status=400)
	except ValidationError as e:
		return Response({"error": e.detail}, status=400)
	except Exception as e:
		return Response({"error": str(e)}, status=500)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def cart_view(request):
#     cart_total_amount = 0
#     if 'cart_data_obj' in request.session:
#         cart_data = request.session['cart_data_obj']

#         for p_id, item in cart_data.items():
#             cart_total_amount += int(item['qty']) * float(item['price'])

#         return Response({"cart_data": cart_data, 'totalcartitems': len(cart_data), 'cart_total_amount': cart_total_amount})
#     else:
#         messages.warning(request, "Your cart is empty")
#         return Response({"error": "Your cart is empty"}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_view(request):
	try:
		if request.method == 'GET':
			cart_total_amount = 0
			if 'cart_data_obj' in request.session:
				cart_data = request.session['cart_data_obj']
				# Calculate total amount
				for p_id, item in cart_data.items():
					cart_total_amount += int(item['qty']) * float(item['price'])
				# Serialize the cart_data.values() as a list
				serializer = CartItemSerializer(data=list(cart_data.values()), many=True)
				serializer.is_valid(raise_exception=True)

				return JsonResponse({
					"cart_data": serializer.data,
					'totalcartitems': len(cart_data),
					'cart_total_amount': cart_total_amount
				})
			else:
				messages.warning(request, "Your cart is empty")
				return JsonResponse({"error": "Your cart is empty"}, status=400)
		else:
			return JsonResponse({"error": "Only GET requests are allowed"}, status=405)
	except Exception as e:
		return JsonResponse({"error": str(e)}, status=500)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def delete_item_from_cart(request):
#     try:
#         product_id = str(request.GET['id'])
#         if 'cart_data_obj' in request.session:
#             if product_id in request.session['cart_data_obj']:
#                 cart_data = request.session['cart_data_obj']
#                 del request.session['cart_data_obj'][product_id]
#                 request.session['cart_data_obj'] = cart_data

#         cart_total_amount = 0
#         if 'cart_data_obj' in request.session:
#             for p_id, item in request.session['cart_data_obj'].items():
#                 cart_total_amount += int(item['qty']) * float(item['price'])

#         # Assuming you have a serializer for your cart items
#         serializer = CartItemSerializer(data=request.session['cart_data_obj'].values(), many=True)
#         serializer.is_valid(raise_exception=True)

#         # Return JSON response with serialized cart data
#         return JsonResponse({
#             "data": serializer.data,
#             'totalcartitems': len(request.session['cart_data_obj']),
#             'cart_total_amount': cart_total_amount
#         })

#     except KeyError as e:
#         return Response({"error": f"Missing parameter: {str(e)}"}, status=400)

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delete_item_from_cart(request):
	try:
		product_id = str(request.GET['id'])
		if 'cart_data_obj' in request.session:
			if product_id in request.session['cart_data_obj']:
				cart_data = request.session['cart_data_obj']
				del request.session['cart_data_obj'][product_id]
				request.session['cart_data_obj'] = cart_data

		cart_total_amount = 0
		if 'cart_data_obj' in request.session:
			cart_items = list(request.session['cart_data_obj'].values())  # Convert dict values to a list
			for item in cart_items:
				cart_total_amount += int(item['qty']) * float(item['price'])

			# Assuming you have a serializer for your cart items
			serializer = CartItemSerializer(data=cart_items, many=True)
			serializer.is_valid(raise_exception=True)

			# Return JSON response with serialized cart data
			return JsonResponse({
				"data": serializer.data,
				'totalcartitems': len(request.session['cart_data_obj']),
				'cart_total_amount': cart_total_amount
			})

	except KeyError as e:
		return Response({"error": f"Missing parameter: {str(e)}"}, status=400)

	except Exception as e:
		return Response({"error": str(e)}, status=500)


# def delete_item_from_cart(request):
#     product_id = str(request.GET['id'])
#     if 'cart_data_obj' in request.session:
#         if product_id in request.session['cart_data_obj']:
#             cart_data = request.session['cart_data_obj']
#             del request.session['cart_data_obj'][product_id]
#             request.session['cart_data_obj'] = cart_data
	
#     cart_total_amount = 0
#     if 'cart_data_obj' in request.session:
#         for p_id, item in request.session['cart_data_obj'].items():
#             cart_total_amount += int(item['qty']) * float(item['price'])

#     context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
#     return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart(request):
	product_id = str(request.GET['id'])
	product_qty = request.GET['qty']

	if 'cart_data_obj' in request.session:
		if product_id in request.session['cart_data_obj']:
			cart_data = request.session['cart_data_obj']
			cart_data[str(request.GET['id'])]['qty'] = product_qty
			request.session['cart_data_obj'] = cart_data
	
	cart_total_amount = 0
	if 'cart_data_obj' in request.session:
		for p_id, item in request.session['cart_data_obj'].items():
			cart_total_amount += int(item['qty']) * float(item['price'])

	context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
	return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})


# @api_view(['POST','GET'])
# @permission_classes([IsAuthenticated])
# def paypal_checkout_view(request):
#     cart_total_amount = 0
#     total_amount = 0

#     # Checking if cart_data_obj session exists
#     if 'cart_data_obj' in request.session:

#         # Getting total amount for Paypal Amount
#         for p_id, item in request.session['cart_data_obj'].items():
#             total_amount += int(item['qty']) * float(item['price'])

#         # Create ORder Object
#         order = CartOrder.objects.create(
#             user=request.user,
#             price=total_amount
#         )

#         # Getting total amount for The Cart
#         for p_id, item in request.session['cart_data_obj'].items():
#             cart_total_amount += int(item['qty']) * float(item['price'])

#             cart_order_products = CartOrderProducts.objects.create(
#                 order=order,
#                 invoice_no="INVOICE_NO-" + str(order.id), # INVOICE_NO-5,
#                 item=item['title'],
#                 image=item['image'],
#                 qty=item['qty'],
#                 price=item['price'],
#                 total=float(item['qty']) * float(item['price'])
#             )

#         payment(cart_total_amount,str(order.id))
#         host = request.get_host()
#         paypal_dict = {
#             'business': settings.PAYPAL_RECEIVER_EMAIL,
#             'amount': cart_total_amount,
#             'item_name': "Order-Item-No-" + str(order.id),
#             'invoice': "INVOICE_NO-" + str(order.id),
#             'currency_code': "USD",
#             'notify_url': 'http://{}{}'.format(host, reverse("core:paypal-ipn")),
#             'return_url': 'http://{}{}'.format(host, reverse("core:payment-completed")),
#             'cancel_url': 'http://{}{}'.format(host, reverse("core:payment-failed")),
#         }

#         paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

#         # cart_total_amount = 0
#         # if 'cart_data_obj' in request.session:
#         #     for p_id, item in request.session['cart_data_obj'].items():
#         #         cart_total_amount += int(item['qty']) * float(item['price'])

#         try:
#             active_address = Address.objects.get(user=request.user, status=True)
#         except:
#             messages.warning(request, "There are multiple addresses, only one should be activated.")
#             active_address = None

#         return Response({"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount, 'paypal_payment_button':paypal_payment_button, "active_address":active_address}, status=status.HTTP_200_OK)


@login_required
def payment_completed_view(request):
	cart_total_amount = 0
	if 'cart_data_obj' in request.session:
		for p_id, item in request.session['cart_data_obj'].items():
			cart_total_amount += int(item['qty']) * float(item['price'])
	return render(request, 'core/payment-completed.html',  {'cart_data':request.session['cart_data_obj'],'totalcartitems':len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})

@login_required
def payment_failed_view(request):
	return Response({"error":"payment faild"}, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def payment(request,cart_total_amount,order_id):
#         # if request.method == "POST":


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout_view(request):
	try:
		cart_total_amount = 0
		total_amount = 0
		# Checking if cart_data_obj session exists
		if 'cart_data_obj' in request.session:
			# Getting total amount for The Cart
			for p_id, item in request.session['cart_data_obj'].items():
				cart_total_amount += int(item['qty']) * float(item['price'])

			# Call the payment function
			try:
				active_address = Address.objects.get(user=request.user, status=True)
			except Address.DoesNotExist:
				messages.warning(request, "There are multiple addresses, only one should be activated.")
				active_address = None

			return Response({
				"cart_data": request.session['cart_data_obj'],
				'totalcartitems': len(request.session['cart_data_obj']),
				'cart_total_amount': cart_total_amount,
				"active_address": active_address
			}, status=status.HTTP_200_OK)

	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def call_back_url(request):
		try:
				data = request.data
				reference = data['reference']

				# Ensure the user is authenticated
				if not request.user.is_authenticated:
						return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

				def verify_payment(request):
						url = 'https://api.paystack.co/transaction/verify/' + reference
						headers = {
								'Authorization': 'Bearer ' + settings.PAYSTACK_SECRET_KEY,
								'Content-type': 'application/json',
								'Accept': 'application/json',
						}
						datum = {
								"reference": reference
						}

						try:
								response = requests.get(url, data=json.dumps(datum), headers=headers)
								response.raise_for_status()  # Raise HTTPError for bad responses
								result = response.json()
								if 'data' not in result:
										return Response({"error": f"Unexpected response format. 'data' key not found: {result}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

								if result['data']['status'] == 'success':
										# Create Order Object
										
										# Check if 'access_code' is present in result['data']
										# if 'access_code' in result['data']:
										#     access_code = result['data']['access_code']
										# else:
										#     # Handle the case where 'access_code' is not present
										#     return Response({"error": "'access_code' not found in response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

										# print(access_code)
										# Continue with the rest of your code...
										
										# Check if 'data' key exists in result and if 'email' key exists in result['data']
										if 'data' in result and 'email' in result['data']['customer']:
												
												CartOrder.objects.filter(user__email=result['data']['customer']['email']).update(paid_status=True)
										else:
												# Handle the case where 'data' or 'email' key is not present
												return Response({"error": "'email' not found in response data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
										total_amount = 0
										for p_id, item in request.session['cart_data_obj'].items():
												total_amount += int(item['qty']) * float(item['price'])
										
										
										order_serializer = OrderSerializer(data={'user': request.user.id, 'price': total_amount})
										order_serializer.is_valid(raise_exception=True)
										order_serializer.save()
										# Obtain the order_id from the newly created order instance
										order_id = order_serializer.data['id']

										order = CartOrder.objects.create(
																user=request.user,
																price=total_amount
														)
										instance = PayHistory.objects.create(
												amount=int(total_amount),
												user=request.user,
												order_id=order.id,
												paystack_charge_id=result['data']['reference'],
												paid=True,
												# paystack_access_code=access_code  # Use the access_code variable here
										)
										# if request.user.is_authenticated:
										#     for p_id, item in request.session['cart_data_obj'].items():
										#         cart_order_products_serializer = CartOrderProductsSerializer(data={
										#             'user': request.user.id,
										#             'order': order.id,
										#             'invoice_no': "INVOICE_NO-" + str(order.id),
										#             'item': item['title'],
										#             'image': item['image'],
										#             'qty': item['qty'],
										#             'price': item['price'],
										#             'total': float(item['qty']) * float(item['price']),
										#             'product_status': 'processing'
										#         })
										#         cart_order_products_serializer.is_valid(raise_exception=True)
										#         cart_order_products_serializer.save()
										# else:
										#     return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

										return response
						except requests.exceptions.HTTPError as errh:
								return Response({"error": f"HTTP Error: {errh}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
						except requests.exceptions.ConnectionError as errc:
								return Response({"error": f"Error Connecting: {errc}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
						except requests.exceptions.Timeout as errt:
								return Response({"error": f"Timeout Error: {errt}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
						except requests.exceptions.RequestException as err:
								return Response({"error": f"Request Exception: {err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

				response = verify_payment(request)
				if response:
						status_code = response.status_code
						if 200 <= status_code < 300:
								return Response({"message": "Payment verification Successfull"},status=status_code)
						else:
								return Response({"message": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
				else:
						return Response({"error": "Payment verification failed. Unable to retrieve response."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		except Exception as e:
				return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def Staff_orders_list(request):
	try:
		if request.method == 'GET':
			orders_list = CartOrder.objects.all().order_by("-id")
			serializer = OrderSerializer(orders_list, many=True)
			staff_list = User.objects.filter(is_staff=True)
			staff = UserSerializer(staff_list, many=True)
			context = {"orders": serializer.data, "staffs": staff.data}
			return Response(context, status=status.HTTP_200_OK)
		elif request.method == 'POST':
			data = request.data
			order = get_object_or_404(CartOrder, pk=data['id'])
			
			# Fetch the User instance based on the email
			staff_email = data['staff']
			staff_user = User.objects.get(email=staff_email)
			
			order.assign_to = staff_user
			order.save()
			
			serializer = OrderSerializer(order)
			context = {"order": serializer.data}
			return Response(context, status=status.HTTP_200_OK)
	except User.DoesNotExist:
		return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
	except CartOrder.DoesNotExist:
		return Response({"error": "CartOrder not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def Staff_list(request):
	try:
		if request.method == 'GET':
			staff_list = User.objects.filter(is_staff=True)
			user_profiles = Profile.objects.filter(user__in=staff_list)
			combined_data = []
			for user in staff_list:
				user_data = UserSerializer(user).data
				profile_data = ProfileSerializer(user_profiles.filter(user=user).first()).data
				combined_data.append({**user_data, **profile_data})
			# staff = UserSerializer(combined_data, many=True)
			context = {"staffs": combined_data}
			return Response(context, status=status.HTTP_200_OK)
		elif request.method == 'POST':
			data = request.data
			username = data.get('username')
			password = data.get('password')
			email = data.get('email')
			retype_password = data.get('retype_password')
			display_name = data.get('display_name')
			staff_role = data.get('staff_role')

			# Check if all required fields are provided
			if not all([username, password, retype_password, display_name, staff_role]):
				return Response({"error": "All required fields must be provided"}, status=status.HTTP_400_BAD_REQUEST)

			# Check if passwords match
			if password != retype_password:
				return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

			if User.objects.filter(email=email).exists():
				return Response({"error": "Email is already taken"}, status=status.HTTP_400_BAD_REQUEST)

			# Check if username is taken
			if User.objects.filter(username=username).exists():
				return Response({"error": "Username is already taken"}, status=status.HTTP_400_BAD_REQUEST)

			# Check if display name is taken
			if Profile.objects.filter(display_name=display_name).exists():
				return Response({"error": "Display name is already taken"}, status=status.HTTP_400_BAD_REQUEST)

			# Create the user
			user = User.objects.create_user(username=username, email=email, password=password, is_staff=True)
			user.profile.display_name = display_name
			user.profile.role = staff_role
			user.save()

			return Response({"message": "Staff user created successfully"}, status=status.HTTP_201_CREATED)
		#   data = request.data
		#   user = get_object_or_404(User, pk=data['id'])
			
		#   # Fetch the User instance based on the email
			
		#   user.assign_to = staff_user
		#   order.save()
			
		#   serializer = OrderSerializer(order)
		#   context = {"order": serializer.data}
		#   return Response(context, status=status.HTTP_200_OK)
	except User.DoesNotExist:
		return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
	except CartOrder.DoesNotExist:
		return Response({"error": "CartOrder not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Account_update(request):
	try:
		if request.method == 'POST':
			data = request.data
			username = data.get('username')
			color = data.get('color')
			display_name = data.get('display_name')
			email = data.get('email')
			staff_role = data.get('staff_role')

			# Get the user object
			user = User.objects.get(username=username)

			# Update the user's profile based on the provided data
			if color:
				user.profile.color = color
			if display_name:
				user.profile.display_name = display_name
			if email:
				user.email = email
			if staff_role:
				user.profile.role = staff_role

			# Save the changes
			user.save()

			return Response({"message": "Staff user details updated successfully"}, status=status.HTTP_200_OK)
	except User.DoesNotExist:
		return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Activities(request):
	try:
		if request.method == 'GET':
			# users = User.objects.filter(is_staff=False)
			# user_profiles = Profile.objects.filter(user__in=users)
			# activities = UserActivity.objects.filter(user=user,product_status=data['status']).order_by("-id")
			activities = UserActivity.objects.all()
			serializer = UserActivitySerializer(activities, many=True)
			context = {"activities": serializer.data}
			return Response(context, status=status.HTTP_200_OK)
		elif request.method == 'POST':
			# data = request.data
			# customer_id = data['id']
			# if not customer_id:
			#   return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
			# customeractivity = UserActivity.objects.filter(pk=customer_id).order_by("-id")
			# # Update the status for each order
			# serializer = UserActivitySerializer(customeractivity, many=True)
			context = {"activities": "none"}
			return Response(context, status=status.HTTP_200_OK)
	except CartOrder.DoesNotExist:
		return Response({"error": "One or more CartOrders not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def customers(request):
	try:
		if request.method == 'GET':
			users = User.objects.filter(is_staff=False, is_superuser=False)
			user_profiles = Profile.objects.filter(user__in=users)
			combined_data = []
			for user in users:
				user_data = UserSerializer(user).data
				profile_data = ProfileSerializer(user_profiles.filter(user=user).first()).data
				combined_data.append({**user_data, **profile_data})
			context = {"customers": combined_data}
			return Response(context, status=status.HTTP_200_OK)
		elif request.method == 'POST':
			data = request.data
			customer_id = data['id']
			if not customer_id:
				return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
			customeractivity = UserActivity.objects.filter(pk=customer_id).order_by("-id")
			# Update the status for each order
			serializer = UserActivitySerializer(customeractivity, many=True)
			context = {"activities": serializer.data}
			return Response(context, status=status.HTTP_200_OK)
	except CartOrder.DoesNotExist:
		return Response({"error": "One or more CartOrders not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customer_orders_list(request):
	try:
		if request.method == 'GET':
			data = request.data
			user_ = data['username']
			user = User.objects.get(username=user_)
			orders_list = CartOrder.objects.filter(user=user,product_status=data['status']).order_by("-id")
			serializer = OrderSerializer(orders_list, many=True)
			context = {"orders": serializer.data}
			return Response(context, status=status.HTTP_200_OK)
		elif request.method == 'POST':
			data = request.data
			order_ids = data.get('ids', [])
			# new_status = data.get('status', '')

			if not order_ids:
				return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
			orders = CartOrder.objects.filter(pk__in=order_ids).order_by("-id")
			
			# Update the status for each order
			for order in orders:
				order.product_status = "cancelled"
				order.save()
			serializer = OrderSerializer(orders, many=True)
			context = {"orders": serializer.data}
			return Response(context, status=status.HTTP_200_OK)
	except CartOrder.DoesNotExist:
		return Response({"error": "One or more CartOrders not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Exchange(request):
	try:
		if request.method == 'POST':
			data = request.data
			order_ids = data.get('ids', [])
			address = data.get('address')
			user_ = data.get('username')
			total_price = data.get('total_price')
			user = User.objects.get(username=user_)

			if not order_ids or not address or not user or not total_price:
				return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)

			with transaction.atomic():
				# Create a single voucher for all orders
				voucher_code = f"AT{secrets.token_hex(4).upper()}"
				discount_price = 50
				voucher_create = Voucher.objects.create(
					user=user,
					code=voucher_code,
					price=float(total_price) - discount_price
				)

				# Update the status for each order
				orders = CartOrder.objects.filter(pk__in=order_ids).order_by("-id")
				for order in orders:
					order.product_status = "processing_exchange"
					order.pickup_address = address
					order.voucher = voucher_create
					order.save()

			serializer = OrderSerializer(orders, many=True)
			context = {"orders": serializer.data}
			return Response(context, status=status.HTTP_200_OK)
	except User.DoesNotExist:
		return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
	except CartOrder.DoesNotExist:
		return Response({"error": "One or more CartOrders not found"}, status=status.HTTP_404_NOT_FOUND)
	except Exception as e:
		return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customer_dashboard(request):
	orders_list = CartOrder.objects.filter(user=request.user,product_status=data['status']).order_by("-id")
	address = Address.objects.filter(user=request.user)

	orders = CartOrder.objects.annotate(month=ExtractMonth("order_date")).values("month").annotate(count=Count("id")).values("month", "count")
	month = []
	total_orders = []

	for i in orders:
		month.append(calendar.month_name[i["month"]])
		total_orders.append(i["count"])

	if request.method == "POST":
		address = request.POST.get("address")
		mobile = request.POST.get("mobile")

		new_address = Address.objects.create(
			user=request.user,
			address=address,
			mobile=mobile,
		)
		messages.success(request, "Address Added Successfully.")
		return redirect("core:dashboard")
	else:
		print("Error")
	
	user_profile = Profile.objects.get(user=request.user)
	print("user profile is: #########################",  user_profile)

	context = {
		"user_profile": user_profile,
		"orders": orders,
		"orders_list": orders_list,
		"address": address,
		"month": month,
		"total_orders": total_orders,
	}
	return Response(context, status=status.HTTP_200_OK)

def order_detail(request, id):
	order = CartOrder.objects.get(user=request.user, id=id)
	order_items = CartOrderProducts.objects.filter(order=order)

	
	context = {
		"order_items": order_items,
	}
	return Response(context, status=status.HTTP_200_OK)


def make_address_default(request):
	id = request.GET['id']
	Address.objects.update(status=False)
	Address.objects.filter(id=id).update(status=True)
	return JsonResponse({"boolean": True})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wishlist_view(request):
	if request.method == 'GET':
		try:
			wish = wishlist_model.objects.all()
			wishlist = WishlistSerializer(wish, many=True)
			context = {
				"w":wishlist.data
			}
			return Response(context, status=status.HTTP_200_OK)
		except Product.DoesNotExist:
			return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
	return Response({}, status.HTTP_400_BAD_REQUEST)


	# w

# def checkout_view(request):
#     if request.method == 'GET':
#         try:
#             brand_instance = Brands.objects.get(vid=vid)
#             brand_serializer = BrandSerializer(brand_instance)
#             context = {
#                 "brand": brand_serializer.data,
#             }
#             return Response(context, status=status.HTTP_200_OK)
#         except Brands.DoesNotExist:
#             return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
#     return Response({}, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
		if request.method == 'GET':
				try:
						product_id = request.GET.get('id')  # Use get to avoid MultiValueDictKeyError
						if not product_id:
								return Response({"error": "'id' parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

						product = Product.objects.get(id=product_id)

						wishlist_item = wishlist_model.objects.filter(product=product, user=request.user).first()

						if wishlist_item:
								return Response({"message": "Item already in wishlist"}, status=status.HTTP_400_BAD_REQUEST)
						else:
								new_wishlist = wishlist_model.objects.create(
										user=request.user,
										product=product,
								)
								return Response({"message": "Item added to wishlist"}, status=status.HTTP_200_OK)
				except Product.DoesNotExist:
						return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
		return Response({}, status.HTTP_400_BAD_REQUEST)



# def remove_wishlist(request):
#     pid = request.GET['id']
#     wishlist = wishlist_model.objects.filter(user=request.user).values()

#     product = wishlist_model.objects.get(id=pid)
#     h = product.delete()

#     context = {
#         "bool": True,
#         "wishlist":wishlist
#     }
#     t = render_to_string("core/async/wishlist-list.html", context)
#     return JsonResponse({"data": t, "w":wishlist})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def remove_wishlist(request):
	pid = request.GET['id']
	wishlist = wishlist_model.objects.filter(user=request.user)
	wishlist_d = wishlist_model.objects.get(id=pid)
	delete_product = wishlist_d.delete()
	
	context = {
		"bool":True,
		"w":wishlist
	}
	wishlist_json = serializers.serialize('json', wishlist)
	t = render_to_string('core/async/wishlist-list.html', context)
	return JsonResponse({'data':t,'w':wishlist_json})





# Other Pages 
def contact(request):
	return render(request, "core/contact.html")


def ajax_contact_form(request):
	full_name = request.GET['full_name']
	email = request.GET['email']
	phone = request.GET['phone']
	subject = request.GET['subject']
	message = request.GET['message']

	contact = ContactUs.objects.create(
		full_name=full_name,
		email=email,
		phone=phone,
		subject=subject,
		message=message,
	)

	data = {
		"bool": True,
		"message": "Message Sent Successfully"
	}

	return JsonResponse({"data":data})


def about_us(request):
	return render(request, "core/about_us.html")


def purchase_guide(request):
	return render(request, "core/purchase_guide.html")

def privacy_policy(request):
	return render(request, "core/privacy_policy.html")

def terms_of_service(request):
	return render(request, "core/terms_of_service.html")

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def send_reset_password_otp(request):
		try:
			if request.method == 'POST':
				email = request.data.get('email')
		
				# Check if the email exists in the database
				try:
					user = User.objects.get(email=email)
				except User.DoesNotExist:
					return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
		
				# Generate OTP
				otp = generate_otp()
		
				# Save the OTP in the user's profile or a separate table
				user.profile.otp = otp
				user.profile.save()
		
				# Send OTP to the user's email
				subject = _('Reset Password OTP')
				message = _('Your OTP for resetting the password is: ') + otp
				from_email = settings.EMAIL_HOST_USER
				recipient_list = [email]
				send_mail(subject, message, from_email, recipient_list, fail_silently=False)
				return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)
		except Exception as e:
			return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def verify_reset_password_otp(request):
		try:
			if request.method == 'POST':
				email = request.data.get('email')
				otp = request.data.get('otp')
		
				# Check if the email exists in the database
				try:
					user = User.objects.get(email=email)
				except User.DoesNotExist:
					return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
		
						# Check if the OTP matches
				if user.profile.otp != otp:
					return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
		
						# Generate a password reset token
				uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
				token = default_token_generator.make_token(user)

				return Response({"uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)
		except Exception as e:
			return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def reset_password(request):
		try:
			if request.method == 'POST':
				uidb64 = request.data.get('uidb64')
				token = request.data.get('token')
				password = request.data.get('password')
		
						# Decode the uidb64 to get the user ID
				try:
					uid = force_str(urlsafe_base64_decode(uidb64))
					user = User.objects.get(pk=uid)
				except (TypeError, ValueError, OverflowError, User.DoesNotExist):
					user = None
		
						# Check if the user exists and the token is valid
				if user is not None and default_token_generator.check_token(user, token):
								# Set the new password
					user.set_password(password)
					user.save()
					return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
				else:
					return Response({"error": "Invalid token or user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
