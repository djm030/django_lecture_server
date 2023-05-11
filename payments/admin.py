from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_date", "calculate_amount")
    list_filter = ("user", "lectures", "payment_date")
    search_fields = ("user__username",)
