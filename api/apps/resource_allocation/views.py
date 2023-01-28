from api.apps.resource_allocation.serializers import ResourceSerializer
from api.apps.utils.permissions import IsAdminOrReadOnly
from api.apps.core.models import (
    Resource,
    Allocation
)

from django.db.models import Q
from django.db.models.deletion import ProtectedError

from rest_framework.exceptions import ValidationError
from rest_framework import viewsets


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = self.queryset.order_by('id')

        if self.action == 'list':
            status_list = self.request.query_params.getlist('status')
            name = self.request.query_params.get('name')

            query = Q()

            if name:
                query &= Q(name__unaccent__icontains=name)

            if status_list:
                if 'active' in status_list and self.request.user.is_staff:
                    query &= Q(is_active=True)
                elif 'inactive' in status_list and self.request.user.is_staff:
                    query &= Q(is_active=False)

                if 'allocated' in status_list:
                    query &= Q(
                        id__in=Allocation.objects.filter(
                            return_date__isnull=True
                        ).values('resource_id')
                    )
                elif 'unallocated' in status_list:
                    query &= Q(
                        id__in=Allocation.objects.filter(
                            return_date__isnull=False
                        ).values('resource_id')
                    )

            queryset = queryset.filter(query)

        return queryset if self.request.user.is_staff else queryset.filter(
            is_active=True
        )

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                {
                    "detail": "Cannot delete because there are allocations linked to the resource."  # noqa: E501
                }
            )
