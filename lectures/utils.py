from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg


def yearly_income(lecture, year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    income = lecture.payments.filter(
        payment_date__range=(start_date, end_date)
    ).aggregate(Sum("amount"))["amount__sum"]
    return income or 0


def monthly_income(lecture, year, month):
    start_date = datetime(year, month, 1)
    end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    income = lecture.payments.filter(
        payment_date__range=(start_date, end_date)
    ).aggregate(Sum("amount"))["amount__sum"]
    return income or 0


def monthly_review_count(lecture, year, month):
    start_date = datetime(year, month, 1)
    end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    review_count = lecture.reviews.filter(
        created_at__range=(start_date, end_date)
    ).count()
    return review_count


def monthly_average_rating(lecture, year, month):
    start_date = datetime(year, month, 1)
    end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    average_rating = lecture.reviews.filter(
        created_at__range=(start_date, end_date)
    ).aggregate(Avg("rating"))["rating__avg"]
    return average_rating or 0
