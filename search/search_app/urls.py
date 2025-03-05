# places_api/urls.py
from django.urls import path
from .views import PlaceSearchView, RegisterView

urlpatterns = [
    path('search/', PlaceSearchView.as_view(), name='place-search'),
    path('register/', RegisterView.as_view(), name='register'),
]
