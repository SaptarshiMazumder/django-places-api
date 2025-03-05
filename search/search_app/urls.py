# places_api/urls.py
from django.urls import path
from .views import PlaceSearchView

urlpatterns = [
    path('search/', PlaceSearchView.as_view(), name='place-search'),
]
