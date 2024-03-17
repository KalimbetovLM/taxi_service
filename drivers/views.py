from rest_framework.generics import CreateAPIView, UpdateAPIView
from drivers.models import Driver, DriverConfirmation,Car, DriversLicense
from drivers.serializers import DriverRegisterSerializer, DriverChangeInfoSerializer, \
DriverChangePhotoSerializer, LoginSerializer, TokenRefreshSerializer, LogOutSerializer, \
ForgotPasswordSerializer, ResetPasswordSerializer, RegisterCarSerializer, UpdateCarPhotoSerializer, \
RegisterLicenseSerializer, UploadLicensePhotoSerializer
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework.views import APIView
import datetime
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from project_taxi.utilities import user_type_regex
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from shared.models import NEW,VERIFIED,DONE
# from shared.models import NEW,VERIFIED,DONE

# Create your views here.

class DriverRegisterView(CreateAPIView):
    queryset = Driver
    permission_classes = (permissions.AllowAny, )
    serializer_class = DriverRegisterSerializer


class DriverVerifyView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self,request,*args,**kwargs):
        driver = self.request.user
        driver = Driver.objects.get(id=driver.id)
        code = self.request.data.get("code")
        self.check_verify(driver,code)
        if driver.auth_status in [NEW,]:
            driver.auth_status = VERIFIED
            driver.save()
            
        return Response(
            data = {
                "success": True,
                "auth_status": driver.auth_status,
                "refresh_token": driver.token()["refresh"],
                "access_token": driver.token()["access"]
            }
        )

    @staticmethod
    def check_verify(driver,code):
        driver = Driver.objects.get(id=driver)
        verify = driver.verify_codes.filter(is_confirmed=False,code=code,driver=driver)
        if not verify:
            data = {
                "message": "This verify code is expired or wrong"
            }
            raise ValidationError(data)            
            
        else:
            verify.update(is_confirmed=True)
        driver.save()
        return True


class GetNewVerifyView(APIView):
    
    def get(self,request,*args,**kwargs):
        driver = self.request.user
        if self.check_verification(driver) == True:
            code = driver.create_verify_code()
            print(f"Your new verify code is {code}")

            return Response({
                "success": True,
                "message": "Verify code has sended"
            })        
        else:
            data = {
                "success": False,
                "message": "Driver not found"
            }
            raise ValidationError(data)

    @staticmethod
    def check_verification(driver):
        verify = DriverConfirmation.objects.filter(expiration_time__gte=datetime.datetime.now(),driver=driver,is_confirmed=False)
        if verify:
            data = {
                "success": False,
                "message": "You can't ask for a new password"
            }
            raise ValidationError(data)
        return True


class DriverChangeInfoView(UpdateAPIView):
    serializer_class = DriverChangeInfoSerializer
    permisson_classes = [permissions.IsAuthenticated, ]
    http_method_names = ["patch", "put"]

    def get_object(self):
        return self.request.user
    
    def update(self,request,*args,**kwargs):
        driver = self.request.user
        super(DriverChangeInfoView,self).update(request,*args,**kwargs)
        data = {
            "success": True,
            "message": "Credentials has been updated successfully",
            "data": {
                "username": driver.username,
                "first_name": driver.first_name,
                "last_name": driver.last_name,
                "password": driver.password,
                "auth_status": driver.auth_status
            }
        }
        return Response(data, status=200)
    
    def partial_update(self,request,*args,**kwargs):
        driver = self.request.user
        super(DriverChangeInfoView,self).partial_update(request,*args,**kwargs)
        data = {
            "success": True,
            "message": "Credentials has been updated successfully",
            "data": {
                "username": driver.username,
                "first_name": driver.first_name,
                "last_name": driver.last_name,
                "password": driver.password,
                "auth_status": driver.auth_status
            }
        }
        return Response(data, status=200)
    

class DriverChangePhotoView(APIView):
    permisson_classes = [permissions.IsAuthenticated, ]

    def put(self,request,*args,**kwargs):
        serializer = DriverChangePhotoSerializer(data=request.data)
        if serializer.is_valid():
            driver = request.user
            serializer.update(driver,serializer.validated_data)
            
            return Response({
                "success": True,
                "message": "Photo has been updated successfully"
            }, status=200)
        else:
            return Response(serializer.errors,status=400)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class TokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

class LogoutView(APIView):
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
                "message": "You have been logged out successfully"
            }
            return Response(data,status=205)
        except TokenError:
            data = {
                "success": False,
                "message": "User not found"
            }
            return Response(data,status=400)
        
        
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = ForgotPasswordSerializer

    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.validated_data.get("driver")
        if driver:
            code = driver.create_verify_code()
            print(f"Your verify code is {code}")        
        return Response({
            "success": True,
            "message": "The new verify code has been sent ",
            "auth_status": driver.auth_status,
            "access": driver.token()["access"],
            "refresh": driver.token()["refresh"]
        },status=200)
    
    
class ResetPasswordView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ResetPasswordSerializer
    http_method_names = ['patch','put']

    def get_object(self):
        return self.request.user
    
    def update(self,request,*args,**kwargs):
        response = super(ResetPasswordView,self).update(request,*args,**kwargs)
        try:
            driver = Driver.objects.get(id=response.data.get("id"))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="No user found")
        return Response({
            "success": True,
            "message": "Password has been updated successfully",
            "auth_status": driver.auth_status,
            "access": driver.token()["access"],
            "refresh": driver.token()["refresh"]
        })
        
        
class RegisterCarView(APIView):
    serializer_class = RegisterCarSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    
    def post(self,request,*args,**kwargs):
        driver = request.user
        data = {
            "number": self.request.data["number"],
            "model": self.request.data["model"],
            "color": self.request.data["color"],
            "owner": driver
        }        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.create(data)
            
        return Response({
            "success": True,
            "message": "The car has been registrated successfully",
            "driver": {
                "id": driver.id,
                "username": driver.username,
            },
            "car": {
                "number": driver.car.number,
                "model": driver.car.model,
                "color": driver.car.color               
            }
        },status=201)
    
class RemoveCarView(APIView):
    permisson_classes = [permissions.IsAuthenticated, ]

    def delete(self,request):
        driver = request.user
        car = Car.objects.get(owner=driver)
        if car:
            car.delete()
            return Response({
                "success": True,
                "message": "Your car has been removed successfully"
            },status=204)
        else:
            return Response({
                "success": False,
                "message": "You have no registered cars"
            })


class UpdateCarPhotoView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def patch(self,request,*args,**kwargs):
        serializer = UpdateCarPhotoSerializer(data = request.FILES)
        if serializer.is_valid():
            car = Car.objects.get(owner=request.user)
            serializer.update(car,serializer.validated_data)
            return Response({
                "success": True,
                "message": "Car's photo has been successfully"
            })
        else:
            return Response(serializer.errors,status=400)


class RegisterLicenseView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request,*args,**kwargs):
        driver = request.user
        if driver.first_name != request.data.get("first_name") or driver.last_name != request.data.get("last_name"):
            raise ValidationError({
                "success": False,
                "message": "You have to finish authentication"
            })
        serializer = RegisterLicenseSerializer(instance=driver,data=request.data)
        if serializer.is_valid():
            serializer.create(driver,serializer.validated_data)
            return Response({
                "success": True,
                "message": "A license has been updated successfully",
                "data": {
                    "license_series": driver.driver_license.series,
                    "license_category": driver.driver_license.category,
                    "driver_first_name": driver.first_name,
                    "driver_last_name": driver.last_name
                }
            })
        else:
            return Response(
                serializer.errors,status=400
            )

class RemoveLicenseView(APIView):

    def delete(self,request,*args,**kwargs):
        driver = request.user
        license = DriversLicense.objects.get(owner=driver)
        if license:
            license.delete()
            return Response({
                "success": True,
                "message": "License has been removed successfully"
            })
        
        else:
            return Response({
                "success": False,
                "message": "You have no registered licenses"
            })
            

class UploadLicensePhotoView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def patch(self,request,*args,**kwargs):
        driver = request.user
        serializer = UploadLicensePhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.upload(driver,serializer.validated_data)
            return Response({
                "success": True,
                "message": "Photo has been uploaded successfully"
            })
        else:
            return Response(serializer.errors,status=400)






