from api.apps.user.serializers import (
    UserSerializer
)

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework import (
    generics,
    viewsets
)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ManageUsersViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = self.queryset

        if self.action == 'list':
            types = self.request.query_params.getlist('type')
            name = self.request.query_params.get('name')

            query = Q()

            if name:
                query &= Q(name__unaccent__icontains=name)

            if types:
                if 'active' in types:
                    query &= Q(is_active=True)
                elif 'inactive' in types:
                    query &= Q(is_active=False)

                if 'admin' in types:
                    query &= Q(is_staff=True)

            queryset = queryset.filter(query)

        return queryset.order_by('id')

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                {
                    "detail": "Unable to delete as there are user-linked allocations."  # noqa: E501
                }
            )
