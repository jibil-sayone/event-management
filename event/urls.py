from django.urls import path
from .views import index, updateEvent, createEvent, fullfill_order, PublishEvent, cancel_order

urlpatterns = [
    path('', index, name='index'),
    path('create_event', createEvent, name="create_event"),
    path('update_event/<str:pk>/', updateEvent, name="update_event"),
    path('payment/<str:pk>/', PublishEvent, name="pay"),
    path('pay_success/<str:pk>/', fullfill_order, name="fullfill"),
    path('pay_fail/', cancel_order, name="fail"),
]