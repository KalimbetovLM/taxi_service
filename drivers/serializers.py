from rest_framework import serializers
from drivers.models import Driver,DriverConfirmation,Car, DriversLicense
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenRefreshSerializer
from project_taxi.utilities import user_type_regex
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from shared.models import NEW,VERIFIED,DONE
# from shared.models import NEW, VERIFIED, DONE


class DriverRegisterSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    def __init__(self,*args,**kwargs):
        super(DriverRegisterSerializer,self).__init__(*args,**kwargs)
        self.fields['phone_number'] = serializers.CharField(required=True)

    class Meta:
        model = Driver
        fields = (
            'id',
            'phone_number',
            'auth_status'
        )
        extra_kwargs = {
            "auth_status": {"read_only": True, "required": False},
            'phone_number': {"required": True}
        }

    def create(self,validated_data):
        driver = Driver.objects.create(
            phone_number = validated_data.get('phone_number')
        )
        code = driver.create_verify_code()
        print(f"Your verify code is {code}")
        driver.save()
        return driver

    def validate(self,data):
        super(DriverRegisterSerializer,self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = data.get('phone_number')
        if user_input:
            data = {
                "phone_number": user_input
            }
        else:
            data = {
                "message": "You must enter a phone number"
            }            
            raise ValidationError(data)
        return data

    def validate_phone_number(self,value):
        if value and Driver.objects.filter(phone_number=value).exists():
            data = {
                "success": False,
                "message": "A user with that phone number already exists"
            }
            raise ValidationError(data)
        return value

    
    def to_representation(self,instance):
        data = super(DriverRegisterSerializer,self).to_representation(instance)
        data.update(instance.token())
        return data
                

class DriverChangeInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True,required=False)
    first_name = serializers.CharField(write_only=True,required=False)
    last_name = serializers.CharField(write_only=True,required=False)
    password = serializers.CharField(write_only=True,required=False)
    confirm_password = serializers.CharField(write_only=True,required=False)

    class Meta:
        model = Driver
        fields = (
            "username",
            "first_name",
            "last_name",
            "password",
            "confirm_password"
        )

    # validating password
    def validate(self,data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")
                            
        if password and confirm_password:
            if password != confirm_password:
                data = {
                    "success": False,
                    "message": "Passwords need to be a same"
                }
                raise ValidationError(data)
            if password:
                validate_password(password)
                validate_password(confirm_password)
        return data
    
    def validate_username(self,username):
        if username:
            if len(username) < 5 or len(username) > 30:
                raise ValidationError({
                    "success": False,
                    "message": "Username's length must be between 5 and 30 characters"
                })
            if username.isdigit():
                raise ValidationError({
                    "success": False,
                    "message": "Username in entirely numeric"
                })
            return username
    
    def validate_first_name(self,first_name):
        if first_name:
            if len(first_name) < 5 or len(first_name) > 30:
                raise ValidationError({
                    "success": False,
                    "message": "First name's length must be between 5 and 30 characters"
                })
        if first_name.isdigit():
            raise ValidationError({
                    "success": False,
                "message": "Your first name is entirely numeric"
            })
        return first_name
    
    def validate_last_name(self,last_name):
        if last_name:
            if len(last_name) < 5 or len(last_name) > 30:
                raise ValidationError({
                    "success": False,
                    "message": "Last name's length must be between 5 and 30 characters"
                })
        return last_name
    
    def update(self,instance,validated_data):
        instance.username = validated_data.get("username",instance.username)
        instance.first_name = validated_data.get("first_name",instance.first_name)
        instance.last_name = validated_data.get("last_name",instance.last_name)
        instance.save()
        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))
        if instance.auth_status == VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance

class DriverChangePhotoSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=[
        'jpg','jpeg','heic','png','heif'
    ])])

    class Meta:
        model = Driver
        fields = [
            "photo"
        ]

    def update(self,instance,validated_data):
        photo = validated_data.get("photo")
        if photo:
            instance.photo = photo
            instance.save()
        return instance


class LoginSerializer(TokenObtainSerializer):

    def __init__(self,*args,**kwargs):
        super(LoginSerializer,self).__init__(*args,**kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False,read_only=True)

    
    def validate(self,data):
        
        self.auth_validate(self,data)        
        data = self.user.token()
        data["username"] = self.user.username
        return data

    @staticmethod    
    def auth_validate(self,data):
        
        userinput = data.get("userinput")
        
        if user_type_regex(userinput) == "username":    
            username = user.username

        elif user_type_regex(userinput) == 'email':
            user = Driver.objects.get(email__iexact=userinput)
            username = user.username
        elif user_type_regex(userinput) == "phone":
            user = Driver.objects.get(phone_number__iexact=userinput)
            username = user.username
        else:
            data = {
                "success": False,
                "message": "You must enter username, email or phone number"
            }
        
            raise NotFound(data)
        
        user = Driver.objects.get(username=username)
        if user is not None:
            self.user = user
        else:
            NotFound({
                "success": False,
                "message": "Wrong credentials"
            })

    def get_user(self,**kwargs):
        users = Driver.objects.filter(**kwargs)
        if not users.exists():
            data = {
                "success": False,
                "message": "User not found"
            }
            PermissionDenied(data)
        return users.first()


class RefreshTokenSerializer(TokenRefreshSerializer):
    
    def validate(self,attrs):   
        data = super().validate(attrs)
        access_token_instance = AccessToken(data["access"])
        user_id = access_token_instance("user_id")
        user = get_object_or_404(Driver,id=user_id)
        update_last_login(None,user)
        return data
    
class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
class ForgotPasswordSerializer(serializers.Serializer):
    userinput = serializers.CharField(write_only=True,required=True)

    def validate(self,attrs):
        userinput = attrs.get("userinput",None)
        if userinput is None:
            raise ValidationError({
                "success": False,
                "message": "User not found"
            })
        driver = Driver.objects.filter(Q(username=userinput) | Q(phone_number=userinput) | Q(email = userinput))
        if not driver.exists():
            raise NotFound({
                "success": False,
                "message": "User not found"
            })
        attrs["driver"] = driver.first()
        return attrs    
    

class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    password = serializers.CharField(min_length=8,write_only=True,required=True)
    confirm_password = serializers.CharField(min_length=8,write_only=True,required=True)

    class Meta:
        model = Driver
        fields = ["id","password","confirm_password"]

    def validate(self,data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError({
                "success": False,
                "message": "Password and confirm password are must be equal to each other"
            })
        if password:
            validate_password(password)
        return data
    
    def update(self,instance,validated_data):
        password = validated_data.pop("password")
        instance.set_password(password)
        return super(ResetPasswordSerializer,self).update(instance,validated_data)
    

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Car

class RegisterCarSerializer(serializers.ModelSerializer):
    color = serializers.CharField(write_only=True, required=True)
    number = serializers.CharField(write_only=True, required=True)
    model = serializers.CharField(write_only=True, required=False)
    driver = serializers.IntegerField(read_only=True, required=False)


    class Meta:
        model = Car
        fields = ["driver", "color", "number", "model"]

    def validate(self, data):
        driver = data.get("driver")
        color = data.get("color")
        number = data.get("number")
        model = data.get("model")

        if model and color and number:
            return data
        else:
            raise ValidationError("You need to enter all the required fields.")

    def create(self, validated_data):
        driver = validated_data.get("owner")        
        car = Car.objects.filter(owner=driver).first()
        if car:
            raise PermissionDenied("You can register only one car. First of registering a new car you have to delete an old car")
        return super(RegisterCarSerializer,self).create(validated_data)
    

class UpdateCarPhotoSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField()

    class Meta:
        model = Car
        fields = ['photo']

    def update(self, instance,validated_data):
        photo = validated_data.get("photo")
        if photo:
            instance.photo = photo
            instance.save()
            return instance
        else:
            raise NotFound("You must enter your car's photo")        
        

class RegisterLicenseSerializer(serializers.ModelSerializer):
    series = serializers.CharField(write_only=True,required=True)
    first_name = serializers.CharField(write_only=True,required=True)
    last_name = serializers.CharField(write_only=True,required=True)
    photo = serializers.ImageField(required=False,validators=[FileExtensionValidator(allowed_extensions=["img","jpg","png","heic","jpeg"])])
    category = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = DriversLicense
        fields = [
            "series",
            "first_name",
            "last_name",
            "photo",
            "category"
        ]

    def validate(self,data):
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        if first_name and last_name:
            return data
        else:
            raise ValidationError({
                "success": False,
                "message": "You need to fill all fields"
            })

    def create(self,instance,data):
        license = DriversLicense.objects.create(
            series = data.get("series"),
            first_name = data.get("first_name"),
            last_name = data.get("last_name"),
            photo = data.get("photo"),
            category = data.get("category"),
            owner = instance
        )
        return license
    

class UploadLicensePhotoSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','heic'])],required=True)

    class Meta:
        model = DriversLicense
        fields = [
            "photo"
        ]

    def validate(self,data):
        photo = data.get("photo")
        if photo:
            return data
        else:
            data = {
                "success": False,
                "message": "You must enter license's photo"
            }
            raise ValidationError(data)
    
    def upload(self,instance,validated_data):
        photo = validated_data.get("photo")
        if photo:
            instance.photo = photo
            instance.save()
            return instance


class SupportSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True)

    class Meta:
        model = Driver
        fields = [
            "text",
            "driver"
        ]
    
    def validate(self,data):
        text = data.get("text")
        if len(text) > 500:
            raise ValidationError({
                "success": False,
                "message": "Text must be less than 500"
            })

    def save(self,validated_data,*args,**kwargs):
        return super(SupportSerializer,self).save(validated_data,*args,**kwargs)


