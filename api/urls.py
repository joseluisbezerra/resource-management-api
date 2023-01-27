from django.contrib import admin
from django.urls import (
    path,
    include
)


urlpatterns = [
    path('admin/', admin.site.urls)
]


# API v1
urlpatterns += [
    path('api/v1/', include(
        [
            path('users/', include('api.apps.user.urls'))
        ]
    ))
]
