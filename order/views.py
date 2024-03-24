from rest_framework import views
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from order.models import Order, COMING, WAY, FINISH, CANCEL
from order.serializers import OrderCreateSerializer, OrderPairSerializer, OrderCancelSerializer,ReviewSerializer
from rest_framework.response import Response
from clients.models import Client
from drivers.models import Driver, DriverStars
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from datetime import datetime,timedelta
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

class OrderCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        return self.request.user
    
    def post(self,request,*args,**kwargs):
        client = self.request.user
        self.request.data["client"] = client.id
        serializer = OrderCreateSerializer(data=self.request.data)
        if serializer.is_valid():
            order = serializer.create(serializer.validated_data)
            return Response({
                "success": True,
                "message": "Looking for a drivers",
                "order_id": order.id,
                "pickup_location": order.pickup_location,
                "dropoff_location": order.dropoff_location,
                "status": order.order_status
            })
        else:
            return Response({
                "success": False,
                "message": "Something went wrong"
            })

class OrderListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request,*args,**kwargs):
        driver = self.request.user
        driver = Driver.objects.get(id=driver.id)
        if not driver:
            raise PermissionDenied(detail="Permission denied")
        orders = Order.objects.filter(order_status=COMING)
        if orders:
            data = {}
            for order in orders:
                buyurtma = {
                    "id": order.id,
                    "pickup_location": order.pickup_location,
                    "dropoff_location": order.dropoff_location
                }
                data["order"] = buyurtma
            return Response(data,status=200)
        else:
            return Response({
                "message": "No orders found"
            })


class OrderPairView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request,*args,**kwargs):        
        driver = self.request.user        
        self.request.data["driver"] = driver
        serializer = OrderPairSerializer(data=self.request.data) 
        if serializer.is_valid():
            order = Order.objects.get(id=serializer.validated_data.get("order_id"))
            serializer.pair(driver,serializer.validated_data)
            return Response({
                "success": True,
                "message": "You successfully accepted an order. You must go to pickup location as soon as possible. Good luck :)",
                "pickup_location": order.pickup_location
            })
        else:
            raise ValidationError({
                "success": False,
                "message": "Something went wrong"
            })

class DriverInPlaceView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['put','patch']

    def patch(self,request,*args,**kwargs):
        driver = self.request.user
        driver = Driver.objects.get(id=driver)        
        order = Order.objects.filter(driver=driver,order_status=COMING).first()        
        if order:
            order.order_status = WAY
            order.start_time = datetime.now()
            
            order.save()
            return Response({
                "success": True,
                "message": "Trip is started",
                "dropoff_location": order.dropoff_location,
                "start_time": order.start_time
            })  
        elif order.order_status == CANCEL:
            return Response({
                "success": True,
                "message": "Client has cancelled an order"
            })
        else:
            return Response({
                "success": False,
                "message": "Trip was already started"
            })        

class TripFinished(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['put','patch']

    def patch(self,request,*args,**kwargs):
        driver = self.request.user
        driver = Driver.objects.get(id=driver)
        order = Order.objects.filter(driver=driver,order_status=WAY).first()
        if order:
            order.order_status = FINISH
            order.end_time = datetime.now()
            # order.total_time = order.end_time - order.start_time
            order.save()
            return Response({
                "success": True,
                "message": "Order has been finished"
            })
        else:
            return Response({
                "success": True,
                "message": "Trip was already finished"
            })


class OrderCancelView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = OrderCancelSerializer

    def delete(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.cancel(serializer.validated_data)
            return Response({
                "success": True,
                "message": "Order has been cancelled successfully"
            })
        else:
            raise NotFound({
                "success": False,
                "message": "Something went wrong"
            })
    

class ReviewView(views.APIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request,*args,**kwargs):
        client = self.request.user
        client = Client.objects.get(id=client)  
        order = Order.objects.filter(client=client).first()
        driver = order.driver
        self.request.data["driver"] = driver.id
        self.request.data["client"] = client.id
        self.request.data["order"] = order.id
        print(self.request.data)
        serializer = ReviewSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            stars = serializer.validated_data.get("stars")
            total_stars = DriverStars.objects.filter(driver=driver)
            total_stars_count = total_stars.count()            
            total_stars_sum = sum([star.stars for star in total_stars])
            total_stars_sum += stars        
            new_average_rating = total_stars_sum / (total_stars_count + 1)            
            driver.rating = new_average_rating
            driver.save()        
            serializer.save()
            print(driver.rating)
            return Response({
                "success": True,
                "message": "Thank you for your feedback"
            })
        else:
            return Response({
                "success": False,
                "message": "Something wnet wrong"
            })
        
        