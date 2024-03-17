from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from clients.models import Client,ClientConfirmation
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenRefreshSerializer
from project_taxi.utilities import user_type_regex
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password

class RegisterClientSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    password = serializers.CharField(required=True,write_only=True)
    phone_number = serializers.CharField(required=True,write_only=True)
    
    class Meta:
        model = Client
        fields = [
            "id",
            "password",
            "phone_number"
        ]

    def validate(self,data):
        super(RegisterClientSerializer,self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        phone_number = data.get("phone_number")
        password = data.get("password")
        if not password and not phone_number:
            raise ValidationError({
                "success": False,
                "message": "You must enter phone number and password"
            })
        if len(password) < 8:
            raise ValidationError({
                "success": False,
                "message": "Your password in invalid"
            })
        if not phone_number.isdigit():
            raise ValidationError({
                "success": False,
                "message": "Your phone number is not numeric"
            })
        if Client.objects.filter(phone_number=phone_number).exists():
            raise ValidationError({
                "success": False,
                "message": "A user with that phone number already exists"
            })
        return data

    def create(self,validated_data):
        client = Client.objects.create(
            phone_number = validated_data.get("phone_number"),
            password = validated_data.get("password")
        )
        code = client.create_verify_code()
        print(f"Your verify code is {code}")
        client.save()
        return client


    def to_representation(self, instance):

        data = super(RegisterClientSerializer,self).to_representation(instance)
        data.update(instance.token())
        return data
    
class ClientChangeInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True,required=False)
    email = serializers.EmailField(write_only=True,required=False)

    class Meta:
        model = Client
        fields = [
            "username",
            "email"
        ]

    def validate(self,data):
        username = data.get("username")
        email = data.get("email")
        if not email and not username:
            raise ValidationError({
                "success": False,
                "message": "You need to enter a values"
            })
        return data
    
    def validate_username(self,username):
        if username:
            if len(username) < 8 or len(username) > 50:
                raise ValidationError({
                    "success": False,
                    "message": "Username chars must be between 8 and 50"
                })
            if username.isdigit():
                raise ValidationError({
                    "success": False,
                    "message": "You username is entirely numeric"
                })
            return username
        
    def validate_email(self,email):
        if email:
            if len(email) < 5 or len(email) > 128:
                raise ValidationError({
                    "success": False,
                    "message": "Your email is in valid"
                })
            return email
        
    def update(self,instance,validated_data):
        instance.username = validated_data.get("username")
        instance.email = validated_data.get("email")
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
            username = userinput
            
        elif user_type_regex(userinput) == 'email':
            user = Client.objects.get(email__iexact=userinput)
            username = user.username
        elif user_type_regex(userinput) == "phone":
            user = Client.objects.get(phone_number__iexact=userinput)
            username = user.username
        else:
            data = {
                "success": False,
                "message": "You must enter username, email or phone number"
            }
        
            raise NotFound(data)
        user = Client.objects.get(username=username)
        
        if user is not None:
            self.user = user
        else:
            NotFound({
                "success": False,
                "message": "Wrong credentials"
            })

    def get_user(self,**kwargs):
        users = Client.objects.filter(**kwargs)
        if not users.exists():
            data = {
                "success": False,
                "message": "User not found"
            }
            PermissionDenied(data)
        return users.first()
    
    
class RefreshTokenSerializer(TokenRefreshSerializer):
    
    def validate(self, attrs):   
        data = super().validate(attrs)
        access_token_instance = AccessToken(data.get("access", None))  # Предполагая, что "access" может быть None
        if access_token_instance:
            user_id = access_token_instance.get("user_id", None)  # Используйте get для безопасного доступа
            if user_id is not None:
                user = get_object_or_404(Client, id=user_id)
                update_last_login(None, user)
        return data

    
class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    userinput = serializers.CharField(write_only=True,required=True)

    def validate(self,attrs):
        userinput = attrs.get("userinput",None)
        if userinput is None:
            raise NotFound({
                "success": False,
                "message": "User not found"
            })
        clients = Client.objects.filter(Q(username=userinput) | Q(email=userinput) | Q(phone_number=userinput))
        if not clients.exists():
            raise NotFound({
                "success": False,
                "message": "User not found"
            })  
        attrs["client"] = clients.first()
        return attrs
    
class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    password = serializers.CharField(min_length=8,max_length=128,required=True)
    confirm_password = serializers.CharField(min_length=8,max_length=128,required=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "password",
            "confirm_password"            
        ]

    def validate(self,data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError({
                "success": False,
                "message": "Passwords must be equal to each other"
            })
        if password:
            validate_password(password)
        return data

    def update(self,instance,validated_data):
        password = validated_data.get("password")
        instance.set_password(password)
        return super(ResetPasswordSerializer,self).update(instance,validated_data)
    


