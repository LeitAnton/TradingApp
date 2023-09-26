from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from user.manager import UserManager


class CreatedDateTime(models.Model):
    """Abstract base model for tracking creation date and time.

    This model adds a 'created_date' field to track the date and time when an object is created.

    """

    created_date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True


class UpdatedDateTime(models.Model):
    """Abstract base model for tracking update date and time.

    This model adds an 'updated_date' field to track the date and time when an object is updated.

    """

    updated_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, CreatedDateTime, UpdatedDateTime):
    """Custom user model for authentication and authorization.

    This model represents a custom user with additional fields such as 'role' and 'token'.

    Attributes:
        RolesChoices (enum): Enumeration of possible user roles.
        role (str): User's role (e.g., 'US' for User, 'AN' for Analyst, 'AD' for Admin).
        username (str): User's username, unique in the system.
        email (str): User's email, unique in the system.
        balance (float): User's balance.
        is_active (bool): Whether the user is active or not.
        is_staff (bool): Whether the user has staff privileges.
        USERNAME_FIELD (str): The field used as the unique identifier for authentication (username).
        objects (UserManager): The manager for the User model.

    """

    class RolesChoices(models.TextChoices):
        USER = 'US', 'User'
        ANALYST = 'AN', 'Analyst'
        ADMIN = 'AD', 'Admin'

    role = models.CharField(
        max_length=2,
        choices=RolesChoices.choices,
        default=RolesChoices.USER,
    )
    username = models.CharField(db_index=True, unique=True, max_length=255)
    email = models.EmailField(db_index=True, unique=True, max_length=255)
    balance = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    objects = UserManager()

    def __str__(self):
        """String representation of the User object.

        Returns:
            str: The username of the User.

        """
        return self.username

    @property
    def token(self):
        """Generate a JSON Web Token (JWT) for the user.

        Generates a JWT with an expiration time of 1 day from the current time.

        Returns:
            str: The generated JWT token.

        """
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """Generate a JSON Web Token (JWT) for the user.

        Generates a JWT with an expiration time of 1 day from the current time.

        Returns:
            str: The generated JWT token.

        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token
