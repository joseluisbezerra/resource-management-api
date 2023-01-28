from api.apps.core.models import (
    Resource,
    Allocation
)

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


class AllocationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, instance):
        return {
            'id': instance.user.id,
            'name': instance.user.name
        }

    class Meta:
        model = Allocation
        fields = (
            'id',
            'user',
            'return_date',
            'allocation_date'
        )
