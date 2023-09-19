from django.contrib.auth import authenticate
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


class LoginSerializer(serializers.Serializer):
    """Serialization of user login. """

    username = serializers.CharField(max_length=255)
    role = serializers.CharField(min_length=2, max_length=2, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)

        if username is None:
            raise serializers.ValidationError(
                'A username is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this username and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'username': user.username,
            'role': user.role,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    """ Performs serialization and deserialization of User objects. """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token',)
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """ Performs an update User. """

        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance
