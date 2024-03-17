from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from project_taxi.utilities import set_id
from uuid import uuid4
from random import randint

# Create your models here.

NEW, VERIFIED, DONE = ("new","verified","done")

AUTH_STATUSES = (
        (NEW, 'New'),
        (VERIFIED, 'Verified'),
        (DONE, 'Done')
    )

class BaseModel(AbstractBaseUser):
    USERNAME_FIELD = 'username'
    ID_FIELD = 'id'
    REQUIRED_FIELDS = ['id','phone_number']

    
    id = models.CharField(default=set_id,primary_key=True,unique=True,max_length=15)
    first_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    username = models.CharField(max_length=50,unique=True)
    auth_status = models.CharField(choices=AUTH_STATUSES,default=NEW,max_length=8)
    email = models.EmailField(max_length=50,unique=True,null=True,blank=True)
    phone_number = models.CharField(max_length=15,unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id
    
    def check_username(self):
        if not self.username:
            temp_username = f"driver-{uuid4().__str__().split('-')[-1]}"
            while BaseModel.objects.filter(username=temp_username).exists():
                temp_username = f"{temp_username}{randint(0,9)}"
            self.username = temp_username

    def check_email(self):
        if self.email:
            normalized_email = self.email.lower()
            self.email = normalized_email
        
    def check_pass(self):
        if not self.password:
            temp_password = "password" + str(set_id)
            self.password = temp_password
        else:
            self.set_password(self.password)

    def hashing_password(self):
        if not self.password.startswith('pbkdf2-sha256'):
            self.set_password(self.password)