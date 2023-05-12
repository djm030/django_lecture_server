from django.db import models
from common.models import CommonModel
from django.conf import settings


# Create your models here.
class Instructor_Application(CommonModel):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="instructor_application",
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        default="",
    )
    career = models.TextField(
        max_length=500,
        blank=True,
        default="",
    )
    image = models.ImageField(
        upload_to="images/",
        blank=True,
        default="",
    )
