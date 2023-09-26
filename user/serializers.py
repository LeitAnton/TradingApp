from django.contrib.auth import authenticate
from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model.

    Serializes user information, including primary key, role, and username.

    """

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'balance',  'role')


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration.

    Serializes user registration data, including username, role, password, and token.
    Also handles user creation.

    """

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
        fields = ['username','email', 'role', 'password', 'token']

    def create(self, validated_data):
        """Create a new user based on validated data.

        Args:
            validated_data (dict): Validated data for user creation.

        Returns:
            User: The newly created user object.

        """
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login.

    Serializes user login data, including username, role, password, and token.
    Also performs user authentication during validation.

    """
    username = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255, read_only=True)
    role = serializers.CharField(min_length=2, max_length=2, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """Validate user login data and perform authentication.

        Args:
            data (dict): User login data to validate.

        Returns:
            dict: Validated user login data including username, role, and token.

        Raises:
            serializers.ValidationError: If validation fails, including missing email or password,
            or if authentication fails.

        """
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

        return {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'token': user.token,
        }


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Serializer for changing user passwords.

    Serializes data for changing user passwords, including the new password.
    Handles updating the user's password.

    """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('role', 'username', 'password',)

    def update(self, instance, validated_data):
        """Update the user's password and any other provided fields.

        Args:
            instance (User): The user instance to update.
            validated_data (dict): Validated data containing the new password.

        Returns:
            User: The updated user object.

        """
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class ResetPasswordSerializer(serializers.ModelSerializer):
    """Serializer for resetting user passwords.

    Serializes data for resetting user passwords, including generating a random password.
    Handles updating the user's password.

    """

    class Meta:
        model = User
        fields = ('role', 'username', 'password',)

    def update(self, instance, validated_data):
        """Reset the user's password to a random value.

        Args:
            instance (User): The user instance to update.
            validated_data (dict): Validated data (not used for resetting password).

        Returns:
            User: The updated user object.

        """
        validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        password = User.objects.make_random_password(length=24)
        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance
