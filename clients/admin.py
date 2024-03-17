# from django.contrib import admin
# from clients.models import Client,ClientConfirmation

# # Register your models here.

# class ClientAdmin(admin.ModelAdmin):
#     list_display = ["id","username","email","phone_number","auth_status"]
#     search_fields = ["id","username"]
#     ordering = ("date_joined", )
# admin.site.register(Client,ClientAdmin)

# class ClientConfirmationAdmin(admin.ModelAdmin):
#     list_display = ["id","code","expiration_time"]
#     search_fields = ["id","code"]
#     list_filter = ["expiration_time"]
#     ordering = ("created_at", )
# admin.site.register(ClientConfirmation,ClientConfirmationAdmin)

