from django.urls import path

from user.views import CreateUserView, LoginUserView


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="user-register"),
    path("login/", LoginUserView.as_view(), name="user-login"),
]

app_name = "user"
