from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Add any additional fields here
    pass

    def __str__(self):
        return self.username
