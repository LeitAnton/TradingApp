from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for the User model.

    This manager provides methods for creating regular users and superusers.

    """

    def create_user(self, username, email, password=None):
        """Create and return a regular user.

        Args:
            username (str): The username for the new user.
            email (str): The email for the new user.
            password (str): The password for the new user (optional).

        Returns:
            User: The newly created regular user.

        Raises:
            TypeError: If the 'username' argument is not provided.
            TypeError: If the 'email' argument is not provided.

        """
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, password=password, email=email)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """Create and return a superuser.

        Args:
            username (str): The username for the new superuser.
            email (str): The email for the new superuser.
            password (str): The password for the new superuser.

        Returns:
            User: The newly created superuser.

        Raises:
            TypeError: If the 'password' argument is not provided.
            TypeError: If the 'email' argument is not provided.

        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        if email is None:
            raise TypeError('Users must have an email address.')

        if username is None:
            raise TypeError('Users must have an username address.')

        user = self.create_user(username=username, password=password, email=email)
        user.role = "AD"
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
