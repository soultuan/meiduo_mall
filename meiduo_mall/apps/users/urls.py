from django.urls import path
from apps.users.views import UsernameCountView,UsermobileCountView,RegisterView

urlpatterns = [
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/',UsermobileCountView.as_view()),
    path('register/',RegisterView.as_view()),
]