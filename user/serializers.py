from rest_framework import serializers

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serialization of user registration and new creation. """
    role = serializers.CharField(
        min_length=2,
        max_length=2,
        read_only=True
    )

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'role', 'password', 'token']

    def create(self, validated_data):
        """Create object of User. """
        return User.objects.create_user(**validated_data)
