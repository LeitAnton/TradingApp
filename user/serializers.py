from django.contrib.auth import authenticate
from rest_framework import serializers

from business.serializers import PortfolioSerializer
from user.models import User
from user.tasks import send_mail_about_reset_password


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model. """

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'role', 'balance')
        read_only_fields = ('pk', 'role', 'balance')


class RegistrationSerializer(UserSerializer):
    """Serializer for user registration. """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('password', 'token')
        read_only_fields = UserSerializer.Meta.read_only_fields + ('token',)

    def create(self, validated_data):
        """Create a new user based on validated data. """
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
        """Validate user login data and perform authentication. """
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


class ChangePasswordSerializer(UserSerializer):
    """Serializer for changing user passwords. """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('password',)
        read_only_fields = UserSerializer.Meta.fields

    def update(self, instance, validated_data):
        """Update the user's password and any other provided fields. """
        password = validated_data.pop('password', None)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class ResetPasswordSerializer(serializers.ModelSerializer):
    """Serializer for resetting user passwords. """

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields
        read_only_fields = UserSerializer.Meta.read_only_fields + ('username', 'email',)

    def update(self, instance, validated_data):
        """Reset the user's password to a random value. """
        password = User.objects.make_random_password(length=24)

        if password is not None:
            instance.set_password(password)

        instance.save()

        send_mail_about_reset_password.delay(
            password=password,
            email=instance.email
        )

        return instance


class OwnUserSerializer(UserSerializer):
    """Serializer for the User model. """
    portfolios = PortfolioSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('portfolios', )
        read_only_fields = fields


class AddBalanceToUserSerializer(serializers.ModelSerializer):
    """Serializer for the User model. """
    amount = serializers.FloatField(write_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('amount', )

    def update(self, instance, validated_data):
        amount = validated_data.pop('amount', 0)
        instance.balance += amount
        instance.save()
        return instance
