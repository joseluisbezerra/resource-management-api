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
            path('', include('api.apps.resource_allocation.urls')),
            path('users/', include('api.apps.user.urls'))
        ]
    ))
]
