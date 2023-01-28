from api.apps.core.models import Resource

from rest_framework import serializers


class ResourceSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        if not kwargs['context']['request'].user.is_staff:
            del self.fields['is_active']

        super().__init__(*args, **kwargs)

    class Meta:
        model = Resource
        fields = (
            'id',
            'name',
            'is_active',
            'is_allocated'
        )
