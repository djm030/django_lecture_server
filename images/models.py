from django.db import models
from users.models import User
from common.models import CommonModel


class ImageType(models.TextChoices):
    INSTRUCTOR_APPLICATION = "INSTRUCTOR_APPLICATION"


class Image(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to="images/")
    image_type = models.CharField(max_length=50, choices=ImageType.choices)

    def __str__(self):
        return f"{self.user.username} - {self.image}"
