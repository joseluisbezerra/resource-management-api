from rest_framework_nested.routers import NestedSimpleRouter
from rest_framework.routers import DefaultRouter
from django.urls import (
    path,
    include
)

from api.apps.resource_allocation import views

router = DefaultRouter()

app_name = 'resource_allocation'

router.register('resources', views.ResourceViewSet)

resource_router = NestedSimpleRouter(
    router,
    r'resources',
    lookup='resource'
)

resource_router.register(
    r'allocations',
    views.AllocationViewSet,
    basename='allocation'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(resource_router.urls))
]
