from django.urls import path
from order.views import OrderCreateView, OrderListView, OrderPairView, DriverInPlaceView, TripFinished, \
OrderCancelView

app_name="order"
urlpatterns = [
    path("create/",OrderCreateView.as_view()),
    path("list/",OrderListView.as_view()),
    path("accept/",OrderPairView.as_view()),
    path("inplace/",DriverInPlaceView.as_view()),
    path("finished/",TripFinished.as_view()),
    path("cancel/",OrderCancelView.as_view()),
]