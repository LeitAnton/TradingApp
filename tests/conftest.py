import pytest
from rest_framework.test import APIClient

from business.models import Currency, Order
from user.models import User
from ddf import G


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    username = 'user1'
    password = 'qwerqwer'
    email = 'test.user1@gmail.com'

    user = G(User, username=username, email=email)
    user.set_password(password)

    return user


@pytest.fixture
def not_active_user():
    username = 'user2'
    password = 'qwerqwer'
    email = 'test.user1@gmail.com'

    user = G(User, username=username, email=email, is_active=False)
    user.set_password(password)

    return user


@pytest.fixture
def analyst():
    username = 'analyst1'
    password = 'qwerqwer'
    role = 'AN'
    email = 'test.analyst1@gmail.com'

    analyst = G(User, username=username, email=email, role=role)
    analyst.set_password(password)

    return analyst


@pytest.fixture
def admin():
    username = 'admin1'
    password = 'qwerqwer'
    role = 'AD'
    email = 'test.admin1@gmail.com'

    admin = G(User, is_superuser=True, username=username, email=email, role=role, is_staff=True)
    admin.set_password(password)

    return admin


@pytest.fixture
def currency():
    return G(Currency)


@pytest.fixture
def order():
    return G(Order)
