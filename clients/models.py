from django.db import models
from django.contrib.auth.models import AbstractUser
from project_taxi.utilities import set_id
from uuid import uuid4
from random import randint
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime,timedelta
from django.contrib.auth.models import Group, Permission
from shared.models import BaseModel
# Create your models here.

class Client(BaseModel):
    given_stars = models.DecimalField(default=5,max_digits=3,decimal_places=2)
    orders_count = models.IntegerField(default=0)
    groups = models.ManyToManyField(Group, related_name='client_groups', related_query_name='client_group')
    user_permissions = models.ManyToManyField(Permission, related_name='client_user_permissions', related_query_name='client_user_permission')
    

    def __str__(self):
        return self.id

    def create_verify_code(self):
        code = "".join([str(randint(0,100) % 10) for _ in range(4) ])
        client = Client.objects.filter(id=self.id).first()
        if client:
            client.verify_codes.create(
                code=code
            )
            return code
        else:
            data = {
                "success": False,
                "message": "User not found"
            }
            raise ValidationError(data)

    
    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    
    def clean(self):
        self.check_username()
        self.check_email()
        self.check_pass()

    def save(self,*args,**kwargs):
        self.clean()
        super(Client,self).save(*args,**kwargs)
    

EXPIRATION_TIME = 5
class ClientConfirmation(models.Model):
    id = models.CharField(default=set_id,primary_key=True,editable=False,max_length=15)
    client = models.ForeignKey("clients.Client",on_delete=models.CASCADE,related_name="verify_codes")
    code = models.CharField(max_length=4)
    expiration_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.client.__str__())
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.expiration_time = datetime.now() + timedelta(minutes=EXPIRATION_TIME)
        super(ClientConfirmation,self).save(*args,**kwargs)
