from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.serializers import ListField, ModelSerializer

from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'amount']


class OrderSerializer(ModelSerializer):
    products = ListField(
        child=OrderItemSerializer(), allow_empty=False, write_only=True
    )
    phonenumber = PhoneNumberField()

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for product_data in products:
            OrderItem.objects.create(order=order, **product_data)

        return order
