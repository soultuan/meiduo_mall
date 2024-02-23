from django.urls import path
from apps.goods.views import IndexView,ListView,ListHotView

urlpatterns = [
    path('index/',IndexView.as_view()),
    path('list/<category_id>/skus/',ListView.as_view()),
    path('hot/<cat_id>/',ListHotView.as_view()),
]