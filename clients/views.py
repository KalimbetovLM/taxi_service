from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from clients.serializers import RegisterClientSerializer, ClientChangeInfoSerializer,LoginSerializer, \
RefreshTokenSerializer, LogOutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from clients.models import Client, ClientConfirmation
from rest_framework import permissions
from rest_framework.decorators import permission_classes
from rest_framework import views
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from datetime import datetime
from rest_framework.generics import UpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

class RegisterClientView(CreateAPIView):
    queryset = Client
    serializer_class = RegisterClientSerializer
    permission_classes = [permissions.AllowAny, ]

class ClientVerifyView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request,*args,**kwargs):
        client_id = self.request.user
        client = Client.objects.get(id=client_id)
        code = self.request.data.get("code")
        self.check_verify(client,code)
        
        client.save()
        return Response({
            "success": True,
            "message": "You welcome",
            "auth_status": client.auth_status,
            "refresh": client.token()["refresh"],
            "access": client.token()["access"]
        })


    @staticmethod
    def check_verify(client,code):
        client = Client.objects.get(id=client)
        verify = client.verify_codes.filter(code=code,client=client,is_confirmed=False).first()
        if not verify:
            data = {
                "message": "Verify code is wrong or expired"
            }
            raise ValidationError(data)
        else:
            verify.is_authenticated = True
        client.save()
        return True

class GetNewVerifyView(views.APIView):
    
    def get(self,request,*args,**kwargs):
        client_id = self.request.user
        client = Client.objects.get(id=client_id)
        if self.check_verification(client) == True:
            code = client.create_verify_code()
            print(f"This is your new verify code {code}")
            return Response({
                "success": True,
                "message": "The new code has been sent successfully"
            })
        else:
            data = {
                "success": False,
                "message": "Something went wrong"
            }
            raise NotFound(data)

    @staticmethod
    def check_verification(client):
        client = Client.objects.get(id=client)
        verify = ClientConfirmation.objects.filter(expiration_time__gte=datetime.now(),client=client,is_confirmed=False)
        if verify:
            data = {
                "success": False,
                "message": "You can't ask for a new verify code now"
            }
            raise ValidationError(data)
        return True

class ClientChangeInfoView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientChangeInfoSerializer    
    http_method_names = ['patch','put']

    def get_object(self):
        return self.request.user
    
    def update(self,request,*args,**kwargs):
        client = self.request.user
        super(ClientChangeInfoView,self).update(request,*args,**kwargs)
        data  = {
            "success": True,
            "message": "Credentials have been successfully",
            "username": client.username,
            "email": client.email,
            "phone_number": client.phone_number,
            "password": client.password
        }
        return Response(data,status=200)
    
    def partial_update(self,request,*args,**kwargs):
        client = self.request.user
        super(ClientChangeInfoView,self).partial_update(request,*args,**kwargs)
        data = {
            "success": True,
            "message": "Credentials have been updated successfully",
            "username": client.username,
            "email": client.email,
            "phone_number": client.phone_number,
            "password": client.password
        }
        return Response(data,status=200)
    

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class TokenRefreshView(TokenRefreshView):
    serializer_class = RefreshTokenSerializer

class LogOutView(views.APIView):
    serializer_class = LogOutSerializer
    permission_classes = [permissions.IsAuthenticated, ]    

    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "success": True,
                "message": "You have been logged out successully"
            }
            return Response(data,status=200)
        except TokenError:
            data = {
                "success": False,
                "message": "User not found"
            }        
            return Response(data,status=400)
    
class ForgotPasswordView(views.APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.validated_data.get("client")
        if client:
            code = client.create_verify_code()
            print(f"Your verify code is {code}")
            return Response({
                "success": True,
                "message": "New verify code has been sent",
                "refresh": client.token()["refresh"],
                "access": client.token()["access"]                
            },status=200)
        else:
            raise NotFound({
                "success": False,
                "message": "User not found"
            })
        

class ResetPasswordView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ["patch","put"]

    def get_object(self):
        return self.request.user
    
    def update(self,request,*args,**kwargs):
        response = super(ResetPasswordView,self).update(request,*args,**kwargs)
        try:
            client = Client.objects.get(id=response.data.get("id"))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="No users found")        
        return Response({
            "success": True,
            "message": "Password reseted",
            "username": client.username,
            "phone_number": client.phone_number,
            "email": client.email
        })


