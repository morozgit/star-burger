import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data
        products = data['products']

    except ValueError:
        return Response({
            'error': 'bla bla bla',
        })
    except KeyError:
        content = {'products': 'Обязательное поле.'}
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if isinstance(products, str):
        content = {'products': 'Ожидался list со значениями, но был получен "str".'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

    if isinstance(products, type(None)):
        content = {'products': 'Это поле не может быть пустым.'}
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(products, list):
        if not products:
            content = {'products': 'Этот список не может быть пустым.'}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    order = Order.objects.create(first_name=data['firstname'],
                                    last_name=data['lastname'],
                                    phone_number=data['phonenumber'],
                                    address=data['address'],
                                    )
    for product in data['products']:
        OrderItem.objects.create(
            order=order,
            product=Product.objects.get(id=product['product']),
            amount=product['quantity']
        )
    return Response(data)
