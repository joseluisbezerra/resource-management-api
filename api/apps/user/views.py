from api.apps.user.serializers import (
    UserSerializer
)

from rest_framework import generics


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
