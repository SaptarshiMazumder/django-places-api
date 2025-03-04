from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SearchHistory, RecommendedPlace


class RecommendedPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedPlace
        fields = ['name', 'address', 'rating', 'user_ratings_count', 
                  'description', 'review_summary', 'distance_m', 
                  'walking_time_min', 'is_best']

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'latitude', 'longitude', 
                  'search_time', 'places']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add the best recommendation manually.
        best_place = instance.places.filter(is_best=True).first()
        representation['best_recommendation'] = (
            RecommendedPlaceSerializer(best_place).data if best_place else None
        )
        return representation

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
