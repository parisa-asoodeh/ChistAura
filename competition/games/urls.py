from django.urls import path
from . import views

urlpatterns = [
    path('create-team/', views.create_team, name='create_team'),
]
