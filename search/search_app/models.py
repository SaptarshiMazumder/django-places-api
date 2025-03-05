from django.db import models

class SearchHistory(models.Model):
    query = models.CharField(max_length=100)  # search term entered by the user
    latitude = models.FloatField()            # detected latitude of the user
    longitude = models.FloatField()           # detected longitude of the user
    search_time = models.DateTimeField(auto_now_add=True)  # timestamp of the search


    def __str__(self):
        return f"{self.query} @ ({self.latitude},{self.longitude})"

class RecommendedPlace(models.Model):
    search = models.ForeignKey(SearchHistory, related_name="places", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    rating = models.FloatField(null=True, blank=True)
    user_ratings_count = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)      # AI-generated detailed description
    review_summary = models.TextField(blank=True)   # AI-generated summary of user reviews
    distance_m = models.IntegerField(null=True, blank=True)      # distance from user in meters
    walking_time_min = models.IntegerField(null=True, blank=True)  # walking time in minutes
    is_best = models.BooleanField(default=False)    # flag for the best recommended place

    def __str__(self):
        return f"{self.name} (Rating: {self.rating})"