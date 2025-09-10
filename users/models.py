from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class User(AbstractUser):
    auth_id = models.CharField(
        max_length=255,
        help_text="A unique token for the user, used for authentication.",
        null=True,
        db_index=True,
    )


class GoogleOAuthCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_uri = models.CharField(max_length=255)
    scopes = models.TextField()

    def __str__(self):
        return f"GoogleOAuthCredentials for {self.user.username}"


# Model to store OAuth state parameters, just to verify correct state. Not related to User directly.
class GoogleOAuthState(models.Model):
    state = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["state"]),
            models.Index(fields=["created_at"]),
        ]


@receiver(post_save, sender=GoogleOAuthState)
def post_save(sender, instance, created, **kwargs):
    if created:
        instance.valid_until = instance.created_at + datetime.timedelta(minutes=15)
        instance.save()
