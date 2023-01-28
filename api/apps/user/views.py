from api.apps.user.serializers import (
    UserSerializer
)

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
    queryset = get_user_model().objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                {
                    "detail": "Unable to delete as there are user-linked allocations."  # noqa: E501
                }
            )
