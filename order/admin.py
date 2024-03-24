from django.contrib import admin
from order.models import Order, Review

# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','pickup_location','dropoff_location','client','driver','order_status']
    search_fields = ['id','driver','client']
    list_filter = ["driver",'order_status']
admin.site.register(Order,OrderAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ["client","driver","order","stars"]
    search_fields = ["client","driver"]
    list_filter = ["stars"]
admin.site.register(Review,ReviewAdmin)