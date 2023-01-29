from api.apps.utils.views import documentation

from django.contrib import admin
from django.urls import (
    include,
    path
)


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Documentation
    path('documentation/', documentation, name="documentation")
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
