from django.urls import path
from drivers.views import DriverRegisterView, DriverVerifyView,GetNewVerifyView, \
    DriverChangeInfoView, DriverChangePhotoView, LoginView, TokenRefreshView, LogoutView, ForgotPasswordView, \
    ResetPasswordView, RegisterCarView,RemoveCarView, UpdateCarPhotoView, RegisterLicenseView, RemoveLicenseView, \
    UploadLicensePhotoView

app_name = "auth"
urlpatterns = [
    path('register/',DriverRegisterView.as_view()),
    path('verify/',DriverVerifyView.as_view()),
    path('new-verify/',GetNewVerifyView.as_view()),
    path('change-info/',DriverChangeInfoView.as_view()),
    path('change-photo/',DriverChangePhotoView.as_view()),
    path('login/',LoginView.as_view()),
    path('token-refresh/', TokenRefreshView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('forgot-password/',ForgotPasswordView.as_view()),
    path('reset-password/',ResetPasswordView.as_view()),
    path('register-car/',RegisterCarView.as_view()),
    path('remove-car/',RemoveCarView.as_view()),
    path('update-photo/',UpdateCarPhotoView.as_view()),
    path('register-license/',RegisterLicenseView.as_view()),
    path('remove-license/',RemoveLicenseView.as_view()),
    path('upload-photo/', UploadLicensePhotoView.as_view()),
    

]

