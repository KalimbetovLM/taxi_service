from django.db import models
from project_taxi.utilities import set_id
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

COMING, WAY, FINISH, CANCEL = ("coming","way","finish", "cancel")
class Order(models.Model):
    ORDER_STATUSES = (
        (COMING,COMING),
        (WAY,WAY),
        (FINISH,FINISH),
        (CANCEL,CANCEL)
    )
    id = models.CharField(default=set_id,primary_key=True,unique=True,max_length=15)
    pickup_location = models.CharField(max_length=100)
    dropoff_location = models.CharField(max_length=100)
    client = models.ForeignKey('clients.Client',on_delete=models.CASCADE,related_name="client")    
    driver = models.ForeignKey('drivers.Driver',on_delete=models.CASCADE,related_name="driver",null=True,blank=True)
    order_status = models.CharField(choices=ORDER_STATUSES,max_length=6,default=COMING)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)
    total_time = models.DateTimeField(null=True)
    cost = models.DecimalField(max_digits=10,decimal_places=5,default=0)

    def __str__(self):
        return self.id
    
    
class Review(models.Model):
    client = models.ForeignKey('clients.Client',on_delete=models.CASCADE,related_name='client_reviews')
    driver = models.ForeignKey('drivers.Driver',on_delete=models.CASCADE,related_name='driver_reviews')
    order = models.ForeignKey('order.Order',on_delete=models.CASCADE,related_name="client_orders")
    text = models.TextField(max_length=500,blank=True,null=True)
    stars = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])


