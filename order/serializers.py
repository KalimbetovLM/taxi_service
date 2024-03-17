from rest_framework import serializers
from order.models import Order, COMING, WAY, FINISH, CANCEL
from clients.models import Client
from rest_framework.exceptions import NotAuthenticated, NotFound
from drivers.models import Driver

# Create your serializers here

class OrderCreateSerializer(serializers.ModelSerializer):
    pickup_location = serializers.CharField(write_only=True,required=True)
    dropoff_location = serializers.CharField(write_only=True,required=True)
    
    class Meta:
        model = Order
        fields = [
            "client", "pickup_location", "dropoff_location"        
        ]
    
    def validate(self,data):
        client = Client.objects.get(id=data.get("client"))
        if not client.is_authenticated:
            raise NotAuthenticated(detail="You need to be authenticated")
        pickup_location = data.get("pickup_location")
        dropoff_location = data.get("dropoff_location")
        if not pickup_location or not dropoff_location:
            raise NotFound(detail="You must enter a pickup and dropoff locations")
        return data

    def create(self,validated_data):
        order = Order.objects.create(
            client = validated_data.get("client"),
            pickup_location = validated_data.get("pickup_location"),
            dropoff_location = validated_data.get("dropoff_location")
        )
        return order


class OrderPairSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "driver"
        ]

    def validate(self,data):
        order_id = data.get("order_id")
        driver_id = data.get("driver")
        driver = Driver.objects.get(id=driver_id)
        if driver.is_authenticated:
            order = Order.objects.filter(id=order_id)
            if order and order.order_status not in [COMING,FINISH,CANCEL]:
                return data
            else:
                raise NotFound(detail="Order not found")
        else:
            raise NotAuthenticated(detail="You are not authenticated")
    
    def pair(self,instance,validated_data):
        instance = Driver.objects.get(id=instance)
        order_id = validated_data.get("order_id")
        order = Order.objects.get(id=order_id)
        order.driver = instance
        order.save()
        return order
    

class OrderCancelSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = Order
        fields = ["order_id"]

    def validate(self,data):
        order_id = data.get("order_id")
        order = Order.objects.filter(id=order_id)
        if order.order_status in [FINISH,CANCEL]:
            raise NotFound(detail="You have no actual orders")
        return data

    def cancel(self,validated_data):
        order_id = validated_data.get("order_id")
        order = Order.objects.get(id=order_id)
        order.order_status = CANCEL
        order.save()

