from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Add any additional fields here
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="user_app_user_set",
        related_query_name="user_app_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_app_user_set",
        related_query_name="user_app_user",
    )

    def __str__(self):
        return self.username
