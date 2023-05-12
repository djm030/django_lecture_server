from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework import routers, permissions


schema_view = get_schema_view(
    openapi.Info(
        title="폼 미쳤다 강의사이트 ",  # 타이틀
        default_version="v1",  # 버전
        description="프로젝트 API 문서",  # 설명
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="djm030@naver.com"),
        license=openapi.License(name="백관열"),
    ),
    validators=["flex"],
    public=True,
    permission_classes=(AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    ## swagger
    path(
        "swagger<str:format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc-v1"
    ),
    ## api
    path("api/v1/users/", include("users.urls")),
    path("api/v1/lectures/", include("lectures.urls")),
    path("api/v1/categories/", include("categories.urls")),
    path("api/v1/videos/", include("videos.urls")),
    path("api/v1/reviews/", include("reviews.urls")),
    path("api/v1/cart/", include("cart.urls")),
    path("api/v1/watchedlectures/", include("watchedlectures.urls")),
    path("api/v1/images/", include("images.urls")),
    path("api/v1/admins/", include("admins.urls"))
    # path("api/v1/ledetaile/", include("ledetailes.urls")),
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("api/v1/accounts/", include("accounts.urls")),
    # path("api/v1/users/", include("dj_rest_auth.urls")),
    # path("api/v1/users/", include("dj_rest_auth.registration.urls")),
    # path("api/v1/users/", include("allauth.urls")),
]
