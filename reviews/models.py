from django.db import models
from common.models import CommonModel
from lectures.models import Lecture
from users.models import User



class Review(CommonModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    lecture = models.ForeignKey(
        Lecture,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    title = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )
    rating = models.PositiveSmallIntegerField()

    content = models.TextField()

    def __str__(self):
        return self.content


class Reply(CommonModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reply",
    )

    review = models.ForeignKey(
        Review,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reply",
    )

    content = models.TextField()

    def __str__(self):
        return self.content
