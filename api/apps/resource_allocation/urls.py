from rest_framework.routers import DefaultRouter
from django.urls import (
    path,
    include
)

from api.apps.resource_allocation import views

router = DefaultRouter()

app_name = 'resource_allocation'

router.register('resources', views.ResourceViewSet)

urlpatterns = [
    path('', include(router.urls))
]
