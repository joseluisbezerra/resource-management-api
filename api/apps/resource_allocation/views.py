from api.apps.utils.permissions import IsAdminOrReadOnly
from api.apps.resource_allocation.serializers import (
    ResourceSerializer,
    AllocationSerializer
)
from api.apps.core.models import (
    Resource,
    Allocation
)

from django.db.models import Q
from django.http.response import Http404
from django.db.models.deletion import ProtectedError

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.order_by('id')
    serializer_class = ResourceSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminOrReadOnly
    )

    def get_queryset(self):
        queryset = self.queryset

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
                    queryset = queryset.exclude(
                        id__in=Allocation.objects.filter(
                            return_date__isnull=True
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


class AllocationViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Allocation.objects.order_by('-allocation_date')
    serializer_class = AllocationSerializer

    def get_resource(self):
        try:
            resource = Resource.objects.get(id=self.kwargs.get("resource_pk"))

            if not resource.is_active and not self.request.user.is_staff:
                raise Resource.DoesNotExist

        except Resource.DoesNotExist:
            raise Http404

        return resource

    def get_queryset(self):
        return self.queryset.filter(resource=self.get_resource())

    def perform_create(self, serializer):
        resource = self.get_resource()

        if not resource.is_active:
            raise ValidationError(
                {'detail': 'Cannot create allocations for inactive resources.'}
            )
        elif resource.is_allocated:
            raise ValidationError(
                {'detail': 'Resource already allocated.'}
            )

        serializer.save(
            resource=resource,
            user=self.request.user
        )
