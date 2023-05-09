from django.urls import path
from . import views

urlpatterns = [
    # 기존 URL 패턴
    path(
        "application/",
        views.InstructorApplicationCreateWithImageAPIView.as_view(),
        name="instructor-application-create",
    ),
    path(
        "application/list/",
        views.InstructorApplicationListAPIView.as_view(),
        name="instructor-application-list",
    ),
    path("application/approval/",views.InstructorApplicationApprovalAPIView.as_view())
]