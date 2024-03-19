from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field


STATUS_CHOICE = (
	("unprocessed", "Unprocessed"),
	("processing", "Processing"),
	("shipped", "Shipped"),
	("delivered", "Delivered"),
	("cancelled", "Cancelled"),
	("processing_exchange", "Processing Exchange"),
	("exchange_dispute", "Exchange Dispute"),
	("exchanged", "Exchanged"),
	("delayed", "Delayed"),
)

STATUS_IMPORTANCE = (
	("normal", "Normal"),
	("high", "High"),
	("low", "Low"),
)

STATUS_ACTION = (
	("active", "Active"),
	("inactive", "Inactive"),

)

STATUS = (
	("draft", "Draft"),
	("disabled", "Disabled"),
	("rejected", "Rejected"),
	("in_review", "In Review"),
	("published", "Published"),
)

# SIZES = (
#     ("xs", "XS"),
#     ("s", "S"),
#     ("m", "M"),
#     ("l", "L"),
#     ("xl", "XL"),
#     ("xxl", "XXL"),
#     ("3xl", "3XL"),
#     ("4xl", "4XL"),
#     ("5xl", "5XL"),
#     ("6xl", "6XL"),
#     ("7xl", "7XL"),
#     ("8xl", "8XL"),
#     ("9xl", "9XL"),
#     ("10xl", "10XL"),
# )


# COLORS = (
#     ("red", "Red"),
#     ("blue", "Blue"),
#     ("green", "Green"),
#     ("yellow", "Yellow"),
#     ("orange", "Orange"),
#     ("purple", "Purple"),
#     ("pink", "Pink"),
#     ("brown", "Brown"),
#     ("gray", "Gray"),
#     ("black", "Black"),
#     ("white", "White"),
#     ("cyan", "Cyan"),
#     ("magenta", "Magenta"),
#     ("teal", "Teal"),
#     ("olive", "Olive"),
#     ("navy", "Navy"),
#     ("maroon", "Maroon"),
#     ("lime", "Lime"),
#     ("indigo", "Indigo"),
#     ("silver", "Silver"),
#     ("gold", "Gold"),
#     ("violet", "Violet"),
#     ("turquoise", "Turquoise"),
#     ("coral", "Coral"),
#     ("lavender", "Lavender"),
#     ("salmon", "Salmon"),
#     ("khaki", "Khaki"),
#     ("aquamarine", "Aquamarine"),
#     ("crimson", "Crimson"),
#     ("chartreuse", "Chartreuse"),
#     ("slategray", "Slate Gray"),
#     ("orchid", "Orchid"),
#     ("peru", "Peru"),
#     ("thistle", "Thistle"),
# )



RATING = (
	(1,  "★☆☆☆☆"),
	(2,  "★★☆☆☆"),
	(3,  "★★★☆☆"),
	(4,  "★★★★☆"),
	(5,  "★★★★★"),
)


def user_directory_path(instance, filename):
	return 'user_{0}/{1}'.format(instance.user.id, filename)


class Color(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name

class Size(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name

class Faq(models.Model):
	title = models.CharField(max_length=200)
	description = CKEditor5Field(config_name='extends', null=True, blank=True)

	def __str__(self):
		return self.title

class Category(models.Model):
	cid = ShortUUIDField(unique=True, length=10, max_length=20,
						 prefix="cat", alphabet="abcdefgh12345")
	title = models.CharField(max_length=100, default="Food")
	image = models.ImageField(upload_to="category", default="category.jpg")
	created_at = models.DateField(auto_now=True)

	class Meta:
		verbose_name_plural = "Categories"

	def category_image(self):
		return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

	def product_count(self):
		return Product.objects.filter(category=self).count()

	def __str__(self):
		return self.title

class SubCategory(models.Model):
	sid = ShortUUIDField(unique=True, length=10, max_length=20,
						 prefix="subcat", alphabet="abcdefgh12345")
	title = models.CharField(max_length=100, default="Subcategory")
	category = models.ForeignKey(
		Category, on_delete=models.CASCADE, related_name='subcategories')
	description = CKEditor5Field(config_name='extends', null=True, blank=True)
	image = models.ImageField(upload_to="subcategory", default="subcategory.jpg")

	class Meta:
		verbose_name_plural = "Subcategories"

	def subcategory_image(self):
		return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

	def product_count(self):
		return Product.objects.filter(category__subcategory=self).count()

	def __str__(self):
		return self.title


class Tags(models.Model):
	pass

class PayHistory(models.Model):
	STATUS_CHOICESD = (('awaiting','Awaiting'), ('declind',"Declind"), ('confirmed',"Confirmed"))
	# STATUS_CHOICES = (('domain','Domain'),('hosting',"Hosting"),('ssl','SSL'), ('pmail',"Pmail"), ('fsd','FSD'), ('maintainers',"Maintainers"), ('orders',"Orders"))
	user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
	paystack_charge_id = models.CharField(max_length=100, default='', blank=True)
	paystack_access_code = models.CharField(max_length=100, default='', blank=True)
	status = models.CharField(max_length=400, choices=STATUS_CHOICESD, default='awaiting')
	paid = models.BooleanField(default=False)
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	date = models.DateTimeField(auto_now_add=True)
	order_id = models.CharField(max_length=200)
 
	def __str__(self):
		return self.user.username



class Brands(models.Model):
	vid = ShortUUIDField(unique=True, length=10, max_length=20,
						 prefix="ven", alphabet="abcdefgh12345")

	title = models.CharField(max_length=100, default="Nestify")
	image = models.ImageField(
		upload_to=user_directory_path, default="vendor.jpg")
	cover_image = models.ImageField(
		upload_to=user_directory_path, default="vendor.jpg")
	# description = models.TextField(null=True, blank=True, default="I am am Amazing Brands")
	description = CKEditor5Field(config_name='extends', null=True, blank=True)

	address = models.CharField(max_length=100, default="123 Main Street.")
	contact = models.CharField(max_length=100, default="+123 (456) 789")
	chat_resp_time = models.CharField(max_length=100, default="100")
	shipping_on_time = models.CharField(max_length=100, default="100")
	authentic_rating = models.CharField(max_length=100, default="100")
	days_return = models.CharField(max_length=100, default="100")
	warranty_period = models.CharField(max_length=100, default="100")
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

	class Meta:
		verbose_name_plural = "Brands"

	def brand_image(self):
		return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

	def __str__(self):
		return self.title


class Product(models.Model):
	pid = ShortUUIDField(unique=True, length=10,
						 max_length=20, alphabet="abcdefgh12345")

	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	category = models.ForeignKey(
		Category, on_delete=models.SET_NULL, null=True, related_name="category")
	subcategory = models.ForeignKey(
		SubCategory, on_delete=models.SET_NULL, null=True, related_name="subcategory") 
	brand = models.ForeignKey(
		Brands, on_delete=models.SET_NULL, null=True, related_name="product")

	title = models.CharField(max_length=100, default="Vintage")
	image = models.ImageField(
		upload_to=user_directory_path, default="product.jpg")
	# description = models.TextField(null=True, blank=True, default="This is the product")
	description = CKEditor5Field(config_name='extends', null=True, blank=True)

	price = models.DecimalField(
		max_digits=99999999999999, decimal_places=2, default="1.99")
	old_price = models.DecimalField(
		max_digits=99999999999999, decimal_places=2, default="2.99")

	specifications = CKEditor5Field(config_name='extends', null=True, blank=True)
	# specifications = models.TextField(null=True, blank=True)
	type = models.CharField(
		max_length=100, default="Organic", null=True, blank=True)
	stock_count = models.CharField(
		max_length=100, default="10", null=True, blank=True)
	life = models.CharField(
		max_length=100, default="100 Days", null=True, blank=True)
	mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)

	tags = TaggableManager(blank=True)
	voucher = models.ManyToManyField("Voucher", blank=True)
	# colors = models.ManyToManyField(max_length=255, choices=COLORS, blank=True)
	# sizes = models.ManyToManyField(max_length=255, choices=SIZES, blank=True)

	# tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)

	product_status = models.CharField(
		choices=STATUS, max_length=10, default="in_review")

	status = models.BooleanField(default=True)
	in_stock = models.BooleanField(default=True)
	featured = models.BooleanField(default=False)
	digital = models.BooleanField(default=False)

	sku = ShortUUIDField(unique=True, length=4, max_length=10,
						 prefix="sku", alphabet="1234567890")

	date = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(null=True, blank=True)
	colors = models.ManyToManyField(Color, blank=True, help_text="Store colors in lowercase")
	sizes = models.ManyToManyField(Size, blank=True, help_text="Store sizes in uppercase")
	
	# def save(self, *args, **kwargs):
	# 	# Convert colors to lowercase if colors_lowercase is True
	# 	if self.colors_lowercase:
	# 		self.colors.set([color.lower() for color in self.colors.all()])

	# 	# Convert sizes to uppercase if sizes_uppercase is True
	# 	if self.sizes_uppercase:
	# 		self.sizes.set([size.upper() for size in self.sizes.all()])

	# 	super().save(*args, **kwargs)

	class Meta:
		verbose_name_plural = "Products"

	def product_image(self):
		return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

	def __str__(self):
		return self.title

	def get_precentage(self):
		new_price = (self.price / self.old_price) * 100
		return new_price


class ProductImages(models.Model):
	images = models.ImageField(
		upload_to="product-images", default="product.jpg")
	product = models.ForeignKey(
		Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "Product Images"

################# Activities delete for staff every 6 months
################# Activities delete for cust every 3 months

############################################## Cart, Order, OrderITems and Address ##################################
############################################## Cart, Order, OrderITems and Address ##################################
############################################## Cart, Order, OrderITems and Address ##################################
############################################## Cart, Order, OrderITems and Address ##################################

class UserActivity(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	activity = models.CharField(max_length=255)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.user.username} - {self.activity} - {self.timestamp}'

# drop_of_address = models.CharField(max_length=200, default="aliceandtiwa.com") new future
class CartOrder(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	price = models.DecimalField(
		max_digits=99999999999999, decimal_places=2, default="1.99")
	paid_status = models.BooleanField(default=False, null=True, blank=True)
	pickup_address = models.CharField(max_length=200, default="aliceandtiwa.com")
	name = models.CharField(max_length=200,default="none")
	order_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	assign_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name="assigned")
	voucher = models.ManyToManyField("Voucher", blank=True)
	importance = models.CharField(
		choices=STATUS_IMPORTANCE, max_length=50, default="normal")
	product_status = models.CharField(
		choices=STATUS_CHOICE, max_length=30, default="processing")
	sku = ShortUUIDField(null=True, blank=True, length=5,
						 prefix="SKU", max_length=20, alphabet="abcdefgh12345")

	class Meta:
		verbose_name_plural = "Cart Order"


class CartOrderProducts(models.Model):
	# user = models.ForeignKey(User, on_delete=models.CASCADE)
	order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
	invoice_no = models.CharField(max_length=200)
	product_status = models.CharField(max_length=200)
	item = models.CharField(max_length=200)
	image = models.CharField(max_length=200)
	qty = models.IntegerField(default=0)
	price = models.DecimalField(max_digits=99999999999999, decimal_places=2, default="1.99")
	total = models.DecimalField(max_digits=99999999999999, decimal_places=2, default="1.99")

	class Meta:
		verbose_name_plural = "Cart Order Items"

	def order_img(self):
		user = self.order.user
		return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))

############################################## Product Revew, wishlists, Address ##################################
############################################## Product Revew, wishlists, Address ##################################
############################################## Product Revew, wishlists, Address ##################################
############################################## Product Revew, wishlists, Address ##################################


class ProductReview(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	product = models.ForeignKey(
		Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
	review = models.TextField()
	rating = models.IntegerField(choices=RATING, default=None)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "Product Reviews"

	def __str__(self):
		return self.product.title

	def get_rating(self):
		return self.rating


class wishlist_model(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "wishlists"

	def __str__(self):
		return self.product.title


class Address(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	mobile = models.CharField(max_length=300, null=True)
	address = models.CharField(max_length=100, null=True)
	status = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = "Address"

# drop_of_address = models.CharField(max_length=200, default="aliceandtiwa.com") new future
class Voucher(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	code = models.CharField(max_length=10, unique=True)
	issued_date = models.DateField(auto_now_add=True)
	issued_time = models.TimeField(auto_now_add=True)
	start_date = models.DateField(auto_now=True)
	start_time = models.TimeField(auto_now=True)
	end_date = models.DateField(auto_now_add=True)
	end_time = models.TimeField(auto_now_add=True)
	price = models.DecimalField(
		max_digits=99999999999999, decimal_places=2, default="0.00")
	status = models.CharField(
		choices=STATUS_ACTION, max_length=100, default="inactive")

	class Meta:
		verbose_name_plural = "Vouchers"

	def __str__(self):
		return self.code


class Slider(models.Model):
	image =  models.ImageField(default=None)
	title = models.CharField(max_length=300, null=True)

	def __str__(self):
		return self.title