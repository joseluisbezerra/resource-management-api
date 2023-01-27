from rest_framework_simplejwt import views as jwt_views
from django.urls import path

from api.apps.user import views


app_name = 'user'


urlpatterns = [
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
