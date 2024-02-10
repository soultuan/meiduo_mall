from django.urls import path
from apps.users.views import UsernameCountView,UsermobileCountView,RegisterView,LoginView,LogoutView,CenterView,EmailView

urlpatterns = [
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/',UsermobileCountView.as_view()),
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('info/',CenterView.as_view()),
    path('emails/',EmailView.as_view()),
    path('emails/verification/',EmailView.as_view()),
]