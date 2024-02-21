from django import views
from django.urls import path, include
from core.views import *

app_name = "core"

urlpatterns = [

    # Homepage
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("product/<pid>/", product_detail_view, name="product-detail"),
    path("slider/", slider, name="slider"),
    path("customers_orders_list_&_statue_update/",Staff_orders_list, name="customers_all_orders"),
    path("customer_orders_&_cancel/",customer_orders_list, name="customer_orders_list"),
    path("customer_exchange/",Exchange, name="customer_exchange"),
    # Category
    
    path("customers/",customers, name="customers"),
    path("Staff_list/",Staff_list, name="Staff_list"),
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list__view, name="category-product-list"),
    path('subcategories/', subcategory_list_view, name='subcategory_list_view'),
    # Brand
    path("brands/", brands_list_view, name="brand-list"),
    path("brand/<vid>/", brand_detail_view, name="brand-detail"),

    # Tags
    path("products/tag/<slug:tag_slug>/", tag_list, name="tags"),

    # Add Review
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),

    # Search
    path("search/", search_view, name="search"),

    # Filter product URL
    path("filter-products/", filter_product, name="filter-product"),

    # Add to cart URL
    path("add-to-cart/", add_to_cart, name="add-to-cart"),

    # Cart Page URL
    path("view-cart/", cart_view, name="view-cart"),

    # Delete ITem from Cart
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),

    # Update  Cart
    path("update-cart/", update_cart, name="update-cart"),

      # Checkout  URL
    path("checkout/", checkout_view, name="checkout"),

    path("call_back_url/", call_back_url, name="call_back_url"),
    # Paypal URL
    path('paypal/', include('paypal.standard.ipn.urls')),

    # Payment Successful
    path("payment-completed/", payment_completed_view, name="payment-completed"),

    # Payment Failed
    path("payment-failed/", payment_failed_view, name="payment-failed"),

    # Dahboard URL
    path("dashboard/", customer_dashboard, name="dashboard"),

    # Order Detail URL
    path("dashboard/order/<int:id>", order_detail, name="order-detail"),

    # Making address defauly
    path("make-default-address/", make_address_default, name="make-default-address"),

    # wishlist page
    path("wishlist/", wishlist_view, name="wishlist"),

    # adding to wishlist
    path("add-to-wishlist/", add_to_wishlist, name="add-to-wishlist"),


    # Remvoing from wishlist
    path("remove-from-wishlist/", remove_wishlist, name="remove-from-wishlist"),


    # path("contact/", contact, name="contact"),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),

    # path("about_us/", about_us, name="about_us"),
    # path("purchase_guide/", purchase_guide, name="purchase_guide"),
    # path("privacy_policy/", privacy_policy, name="privacy_policy"),
    # path("terms_of_service/", terms_of_service, name="terms_of_service"),
]