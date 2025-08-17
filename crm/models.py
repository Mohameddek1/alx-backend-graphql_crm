
# Create your models here.

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

class Customer(models.Model):
	name = models.CharField(max_length=100)
	email = models.EmailField(unique=True)
	phone = models.CharField(max_length=20, blank=True, null=True,
		validators=[RegexValidator(
			regex=r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$',
			message='Phone must be in +1234567890 or 123-456-7890 format.'
		)]
	)

class Product(models.Model):
	name = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
	stock = models.PositiveIntegerField(default=0)

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
	products = models.ManyToManyField(Product, related_name='orders')
	order_date = models.DateTimeField(auto_now_add=True)
	total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
