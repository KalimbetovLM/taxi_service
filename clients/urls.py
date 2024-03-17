from django.urls import path
from clients.views import RegisterClientView, ClientVerifyView, GetNewVerifyView, ClientChangeInfoView, LoginView, \
TokenRefreshView, LogOutView, ForgotPasswordView, ResetPasswordView

app_name = "clients"
urlpatterns = [
    path("register/",RegisterClientView.as_view()),
    path("verify/",ClientVerifyView.as_view()),
    path("new-verify/",GetNewVerifyView.as_view()),
    path("change-info/",ClientChangeInfoView.as_view()),
    path("login/",LoginView.as_view()),
    path("refresh/",TokenRefreshView.as_view()),
    path("logout/",LogOutView.as_view()),
    path("forgot-password/",ForgotPasswordView.as_view()),
    path("reset-password/",ResetPasswordView.as_view()),
]