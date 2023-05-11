from django.db import models

from lectures.models import Lecture


class Payment(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payment",
    )
    lectures = models.ManyToManyField(
        Lecture,
        related_name="payments",
        blank=True,
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 새로운 결제가 생성될 때만 실행
        if self._state.adding:
            amount = self.calculate_amount()

            # 각 강의별 판매 금액 업데이트
            for lecture in self.lectures.all():
                calculated_lecture = lecture.calculatedlecture.first()
                calculated_lecture.total_sales += amount
                calculated_lecture.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.payment_date} - 결제내역"

    def calculate_amount(self):
        return sum(lecture.lectureFee for lecture in self.lectures.all())
