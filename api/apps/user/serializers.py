from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        if not kwargs['context']['request'].user.is_staff:
            del self.fields['is_active']
            del self.fields['is_staff']

        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = (
            'name',
            'email',
            'password',
            'is_active',
            'is_staff'
        )
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate_password(self, value):
        validate_password(password=value, user=User)

        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
