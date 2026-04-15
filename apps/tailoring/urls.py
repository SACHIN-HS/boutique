from django.urls import path
from . import views

urlpatterns = [
    path('', views.tailoring_view, name='tailoring'),
]
