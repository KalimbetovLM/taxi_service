from django.contrib import admin
from drivers.models import Driver, DriverConfirmation
# Register your models here.

class DriverAdmin(admin.ModelAdmin):
    list_display = ["id","username","email","phone_number","auth_status"]
    search_fields = ["id","username"]
    ordering = ("date_joined", )
admin.site.register(Driver,DriverAdmin)

class DriverConfirmationAdmin(admin.ModelAdmin):
    list_display = ["id","code","expiration_time"]
    search_fields = ["id","code"]
    list_filter = ["expiration_time"]
    ordering = ("created_at",)
admin.site.register(DriverConfirmation,DriverConfirmationAdmin)


