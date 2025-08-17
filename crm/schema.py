import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    customer = graphene.Field(CustomerType)
    products = graphene.List(ProductType)
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            return CreateCustomer(customer=None, message="Email already exists")
        try:
            customer = Customer(name=input.name, email=input.email, phone=input.phone)
            customer.full_clean()
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except ValidationError as e:
            return CreateCustomer(customer=None, message=str(e))

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CreateCustomerInput, required=True)
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    def mutate(self, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for i, data in enumerate(input):
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Row {i+1}: Email {data.email} already exists")
                    continue
                try:
                    customer = Customer(name=data.name, email=data.email, phone=data.phone)
                    customer.full_clean()
                    customer.save()
                    created.append(customer)
                except ValidationError as e:
                    errors.append(f"Row {i+1}: {str(e)}")
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)
    product = graphene.Field(ProductType)
    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            raise Exception("Stock cannot be negative")
        product = Product(name=input.name, price=input.price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)
    order = graphene.Field(OrderType)
    message = graphene.String()
    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(order=None, message="Invalid customer ID")
        products = Product.objects.filter(pk__in=input.product_ids)
        if products.count() != len(input.product_ids):
            return CreateOrder(order=None, message="One or more product IDs are invalid")
        if not products:
            return CreateOrder(order=None, message="At least one product must be selected")
        order_date = input.order_date or timezone.now()
        order = Order(customer=customer, order_date=order_date)
        order.save()
        order.products.set(products)
        total = sum([p.price for p in products])
        order.total_amount = total
        order.save()
        return CreateOrder(order=order, message="Order created successfully")

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)
    def resolve_customers(self, info):
        return Customer.objects.all()
    def resolve_products(self, info):
        return Product.objects.all()
    def resolve_orders(self, info):
        return Order.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
