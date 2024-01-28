from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItemQuerySet(models.QuerySet):
    def get_restaurants_by_order(self, order_id):
        order = Order.objects.select_related('restaurant').get(pk=order_id)
        if order.restaurant:
            return {order.restaurant}

        product_ids = order.items.all().values_list('product_id', flat=True)
        restaurants = Restaurant.objects.filter(
            menu_items__product_id__in=product_ids,
            menu_items__availability=True
        ).distinct()

        restaurants = restaurants.filter(menu_items__product_id__in=product_ids)

        return restaurants.distinct()



class RestaurantMenuItem(models.Model):
    available = RestaurantMenuItemQuerySet.as_manager()
    objects = models.Manager()
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )
    objects = models.Manager()

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('FS', 'Обработанный'),
        ('PR', 'Необработанный'),
    ]
    PAYMENT_CHOICES = [
        ('CASH', 'Наличные'),
        ('CARD', 'Электронно'),
    ]
    firstname = models.CharField(
        verbose_name='имя',
        max_length=50
    )
    lastname = models.CharField(
        verbose_name='фамилия',
        max_length=50
    )
    phonenumber = PhoneNumberField(region="RU")

    address = models.CharField(
        verbose_name='адрес',
        max_length=50,
        db_index=True
    )

    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        db_index=True,
        default='Необработанный',
        verbose_name='статус'
    )

    payment = models.CharField(
        max_length=30,
        choices=PAYMENT_CHOICES,
        db_index=True,
        default='Электронно',
        verbose_name='способ оплаты'
    )

    comment = models.TextField(
        blank=True,
        verbose_name='комментарий',
        )

    registered_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Зарегистрирован в',
        db_index=True,
        )

    called_at = models.DateTimeField(
        verbose_name='Позвонить в',
        db_index=True,
        null=True, blank=True,
        )

    delivered_at = models.DateTimeField(
        verbose_name='Доставлен в',
        db_index=True,
        null=True, blank=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return self.firstname


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        verbose_name='заказ',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='items',
        verbose_name='продукт',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.IntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1)]
    )
