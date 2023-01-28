from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from django.urls import (
    path,
    include
)

from api.apps.user import views

router = DefaultRouter()

app_name = 'user'


router.register('', views.ManageUsersViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path(
        'me/',
        views.ManageUserView.as_view(),
        name='me'
    ),

    path(
        'token/',
        jwt_views.TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'token/refresh/',
        jwt_views.TokenRefreshView.as_view(),
        name='token_refresh'
    )
]
