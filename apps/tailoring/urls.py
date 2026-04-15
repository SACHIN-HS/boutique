from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.tailor_add, name='tailor_add'),
    path('', views.tailor_view, name='tailor_view'),
    path('job/<int:job_pk>/action/', views.tailor_job_action, name='tailor_job_action'),
]
