from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.serializers import ListField, ModelSerializer

from .models import Order, OrderItem, Product


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    phonenumber = PhoneNumberField()
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product in products:
            OrderItem.objects.create(order=order,
                                     price=product['product'].price,
                                     **product,
                                     )
        return order
