from django.db import models
from django.contrib.auth.models import AbstractUser
from project_taxi.utilities import set_id
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from random import randint
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime,timedelta
from rest_framework.exceptions import ValidationError
from colorfield.fields import ColorField
from django.contrib.auth.models import Group, Permission
from shared.models import BaseModel, AUTH_STATUSES, NEW

# Create your models here.

class Car(models.Model):
    id = models.CharField(default=set_id,primary_key=True,editable=False,unique=True)
    owner = models.OneToOneField("drivers.Driver",on_delete=models.CASCADE,related_name="car")
    color = ColorField()
    photo = models.ImageField(default="cars/default_car_photo.jpg", upload_to="cars/")
    number = models.CharField()
    model = models.CharField()

    def __str__(self):
        return f"{self.id}"

    def full_info(self):
        return f"Color:{self.color} \n Model:{self.model} \n Number:{self.number}"
    
    
B,BC = ("b","bc")
class DriversLicense(models.Model):
    CATEGORIES = (
        (B,B),
        (BC,BC)
    )

    id = models.CharField(default=set_id,primary_key=True,editable=False,unique=True)
    owner = models.OneToOneField("drivers.Driver",on_delete=models.CASCADE,related_name="driver_license")
    series = models.CharField(default=0)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='drivers/licenses/',default="drivers/default_driver_image.jpg")
    category = models.CharField(max_length=2,choices=CATEGORIES)
    
    def __str__(self):
        return f"{self.id}"




class Driver(BaseModel):

    photo = models.ImageField(default='drivers/default_driver_image/png',upload_to='drivers/')
    given_stars = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],default=1)
    rating = models.DecimalField(default=0,decimal_places=2,max_digits=3)
    
    groups = models.ManyToManyField(Group, related_name='driver_groups', related_query_name='driver_group')
    user_permissions = models.ManyToManyField(Permission, related_name='driver_user_permissions', related_query_name='driver_user_permission')

    def __str__(self):
        return self.id
    
    # @property
    # def auth_status(self):
    #     return self.auth_status
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def create_verify_code(self):
        code = "".join([str(randint(0,100) % 10) for _ in range(4) ])
        print(type(code))
        print(code)
        driver = Driver.objects.filter(id=self.id).first()
        if driver:
            driver.verify_codes.create(
                code=code
            )
            return code
        else:
            data = {
                "success": False,
                "message": "The Driver not found"
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
        self.hashing_password()
        
    def save(self,*args,**kwargs):
        self.clean()
        super(Driver,self).save(*args,**kwargs)
        
EXPIRATION_TIME = 5
class DriverConfirmation(models.Model):
    id = models.CharField(default=set_id,primary_key=True,max_length=9)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=4)
    driver = models.ForeignKey('drivers.Driver',on_delete=models.CASCADE,related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.driver.__str__())
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.expiration_time = datetime.now() + timedelta(minutes=EXPIRATION_TIME)
        super(DriverConfirmation,self).save(*args,**kwargs)
