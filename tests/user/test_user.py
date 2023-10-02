import pytest
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import PermissionDenied

from user.models import User


class TestUserViewSet:
    def take_headers(self, token):
        headers = {'Authorization': f'Bearer {token}'}
        return headers

    @pytest.fixture
    def url(self):
        url = '/api/users/user/'
        return url

    @pytest.mark.django_db
    def test_login_ok(self, client, user, url):
        password_to_check = 'qwerqwer'
        if check_password(password_to_check, user.password):
            response = client.post(url + 'login/', {
                'username': user.username,
                'password': password_to_check
            })
            data = response.data

            assert response.status_code == 200
            assert data['username'] == user.username
            assert data['role'] == user.role
            assert 'token' in data
        else:
            assert False

    @pytest.mark.django_db
    def test_login_fail(self, client, url):
        response = client.post(url + 'login/', {
            'username': 'test1',
            'password': 'qwerqwer'
        })

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_own_ok(self, client, user, analyst, url):
        for person in (user, analyst):
            headers = self.take_headers(person.token)

            response = client.get(url + 'own_user/', headers=headers)
            data = response.data

            assert response.status_code == 200
            assert data['username'] == person.username
            assert data['email'] == person.email
            assert data['role'] == person.role

    @pytest.mark.django_db
    def test_own_permission_denied(self, client, url):
        try:
            client.get(url + 'own_user/')
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_register(self, client, url):
        payload = {
            'username': 'test1',
            'email': 'test.user@gmail.com',
            'password': 'qwerqwer'
        }

        response = client.post(url + 'registration/', payload)
        data = response.data

        assert data['username'] == payload['username']
        assert data['email'] == payload['email']
        assert data['balance'] == 0.0
        assert 'password' not in data

    @pytest.mark.django_db
    def test_register_fail(self, client, url):
        payload = {
            'username': 'test1',
            'password': 'qwerqwer'
        }

        response = client.post(url + 'registration/', payload)

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_register_user_already_exist(self, client, user, url):
        response = client.post(url + 'registration/', {
            'username': user.username,
            'email': user.email,
            'password': user.password
        })

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_user_list(self, client, analyst, url):
        headers = self.take_headers(analyst.token)

        response = client.get(url, headers=headers)

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_user_list_permission_denied(self, client, user, url):
        headers = self.take_headers(user.token)

        response = client.get(url, headers=headers)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_block_user(self, client, admin, user, url):
        headers = self.take_headers(admin.token)
        response = client.patch(url + f'{user.id}/block_user/', headers=headers)
        user = User.objects.get(username=user.username)

        assert response.status_code == 200
        assert user.is_active is not True

    @pytest.mark.django_db
    def test_block_user_permission_denied(self, client, user, analyst, url):
        for person in (user, analyst):
            headers = self.take_headers(person.token)
            response = client.patch(url + f'{person.id}/block_user/', headers=headers)

            person = User.objects.get(username=person.username)
            assert response.status_code == 403
            assert person.is_active is True

    @pytest.mark.django_db
    def test_not_active_user(self, client, not_active_user, url):
        headers = self.take_headers(not_active_user.token)
        try:
            client.patch(url + 'own_user/', headers=headers)
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_change_password(self, client, user, url):
        headers = self.take_headers(user.token)
        previous_password = 'qwerqwer'
        new_password = 'qwerqwer1'

        response1 = client.post(url + 'login/', {
            'username': user.username,
            'password': previous_password
        })
        response2 = client.patch(url + 'change_password/', headers=headers, data={'password': new_password})
        response3 = client.post(url + 'login/', {
            'username': user.username,
            'password': previous_password
        })
        response4 = client.post(url + 'login/', {
            'username': user.username,
            'password': new_password
        })

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 400
        assert response4.status_code == 200

    @pytest.mark.django_db
    def test_change_password_permission_denied(self, client, url):
        new_password = 'qwerqwer1'
        try:
            client.patch(url + 'change_password/', data={'password': new_password})
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_reset_password(self, client, user, url):
        headers = self.take_headers(user.token)
        previous_password = 'qwerqwer'

        response1 = client.post(url + 'login/', {
            'username': user.username,
            'password': previous_password
        })
        response2 = client.put(url + 'reset_password/', headers=headers)
        response3 = client.post(url + 'login/', {
            'username': user.username,
            'password': previous_password
        })

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 400

    @pytest.mark.django_db
    def test_reset_password_permission_denied(self, client, url):
        try:
            client.patch(url + 'reset_password/')
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False
