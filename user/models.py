from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from user.manager import UserManager


class CreatedDateTime(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True


class UpdatedDateTime(models.Model):
    updated_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, CreatedDateTime, UpdatedDateTime):
    class RolesChoices(models.TextChoices):
        USER = 'US', _('User')
        ANALYST = 'AN', _('Analyst')
        ADMIN = 'AD', _('Admin')

    role = models.CharField(
        max_length=2,
        choices=RolesChoices.choices,
        default=RolesChoices.USER,
    )
    username = models.CharField(db_index=True, max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        """Call the _generate_jwt_token function to generate token. """
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """Generate jwt token. """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token
