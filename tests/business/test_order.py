import pytest
from django_dynamic_fixture import G
from rest_framework.exceptions import PermissionDenied

from business.models import Order


class TestOrderViewSet:
    def take_headers(self, token):
        return {'Authorization': f'Bearer {token}'}

    @pytest.fixture
    def url(self):
        return '/api/business/order/'

    @pytest.fixture
    def order_payload(self, user, currency):
        payload = {
            "currency": currency.id,
            "create_by_price_or_quantity": "Q",
            "action": "B",
            "quantity": 1000,
            "price": 1000,
            "match_price_per_currency_quantity": currency.price_per_quantity,
            "order_type": "M",
            "user": user.id
        }
        return payload

    @pytest.fixture
    def order_admin_list(self, admin):
        return G(Order, user=admin, n=2)

    @pytest.fixture
    def order_user_list(self, user):
        return G(Order, user=user, n=2)

    @pytest.fixture
    def user_s_order(self, user):
        return G(Order, user=user)

    @pytest.mark.django_db
    def test_list_ok(self, client, user, admin, analyst, order_admin_list, order_user_list, url):
        for person in (user, analyst, admin):
            headers = self.take_headers(person.token)

            response = client.get(url, headers=headers)
            pk_list = [order['pk'] for order in response.data]

            assert response.status_code == 200
            assert all(order.id in pk_list for order in order_user_list)
            if person == user:
                assert all(order.id not in pk_list for order in order_admin_list)
            else:
                assert all(order.id in pk_list for order in order_admin_list)

    @pytest.mark.django_db
    def test_list_permission_denied(self, client, url):
        try:
            client.get(url)
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_create_ok(self, client, user, order_payload, url):
        headers = self.take_headers(user.token)

        response = client.post(url, headers=headers, data=order_payload)

        assert response.status_code == 201
        assert response.data['user'] == user.username
        assert response.data['currency'] == order_payload['currency']
        assert response.data['price'] == order_payload['price']
        assert response.data['action'] == order_payload['action']
        assert response.data['quantity'] == order_payload['quantity']
        assert response.data['order_type'] == order_payload['order_type']
        assert response.data['create_by_price_or_quantity'] == order_payload['create_by_price_or_quantity']
        assert response.data['match_price_per_currency_quantity'] == order_payload['match_price_per_currency_quantity']

    @pytest.mark.django_db
    def test_create_permission_denied(self, client, user, order_payload, url):
        try:
            client.post(url, data=order_payload)
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_create_required_field(self, client, user, url):
        headers = self.take_headers(user.token)

        response = client.post(url, headers=headers)

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_retrieve_order_by_user_ok(self, client, user, user_s_order, url):
        headers = self.take_headers(user.token)

        response = client.get(url + f'{user_s_order.id}/', headers=headers)

        assert response.status_code == 200
        assert response.data['user'] == user.id
        assert response.data['currency'] == user_s_order.currency.id
        assert response.data['price'] == user_s_order.price
        assert response.data['quantity'] == user_s_order.quantity

    @pytest.mark.django_db
    def test_retrieve_order_by_not_author(self, client, user, order, url):
        headers = self.take_headers(user.token)

        response = client.get(url + f'{order.id}/', headers=headers)

        assert response.status_code == 403

    @pytest.mark.django_db
    def test_retrieve_order_by_analyst_admin_ok(self, client, analyst, admin, order, url):
        for person in (analyst, admin):
            headers = self.take_headers(person.token)

            response = client.get(url + f'{order.id}/', headers=headers)

            assert response.status_code == 200
            assert response.data['user'] != person.id
            assert response.data['currency'] == order.currency.id
            assert response.data['price'] == order.price
            assert response.data['quantity'] == order.quantity

    @pytest.mark.django_db
    def test_retrieve_permission_denied(self, client, order, url):
        try:
            client.get(url + f'{order.id}/')
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_put_ok(self, client, user, admin, user_s_order, order_payload, url):
        for person in (user, admin):
            headers = self.take_headers(person.token)

            response = client.put(url + f'{user_s_order.id}/', headers=headers, data=order_payload)

            assert response.status_code == 200
            assert response.data['user'] == person.id
            assert response.data['currency'] == order_payload['currency']
            assert response.data['price'] == order_payload['price']
            assert response.data['action'] == order_payload['action']
            assert response.data['quantity'] == order_payload['quantity']

    @pytest.mark.django_db
    def test_put_order_by_not_author(self, client, user, order, order_payload, url):
        headers = self.take_headers(user.token)

        response = client.put(url + f'{order.id}/', headers=headers, data=order_payload)

        assert response.status_code == 403

    @pytest.mark.django_db
    def test_put_permission_denied(self, client, order, order_payload, url):
        try:
            client.put(url + f'{order.id}/', data=order_payload)
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_put_not_full_update(self, client, user, user_s_order, url):
        headers = self.take_headers(user.token)
        quantity = 1999

        response = client.put(url + f'{user_s_order.id}/', headers=headers, data={'quantity': quantity})

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_patch_ok(self, client, admin, order, url):
        headers = self.take_headers(admin.token)
        action = 'S'

        response = client.patch(url + f'{order.id}/', headers=headers, data={'action': action})

        assert response.status_code == 200
        assert response.data['user'] == order.user.id
        assert response.data['user'] != admin.id
        assert response.data['action'] == action

    @pytest.mark.django_db
    def test_patch_permission_denied(self, client, user, order, url):
        headers = self.take_headers(user.token)
        action = 'S'

        response = client.patch(url + f'{order.id}/', headers=headers, data={'action': action})

        assert response.status_code == 403

    @pytest.mark.django_db
    def test_destroy_ok(self, client, user, user_s_order, url):
        headers = self.take_headers(user.token)

        response = client.delete(url + f'{user_s_order.id}/', headers=headers)

        assert response.status_code == 204

    @pytest.mark.django_db
    def test_destroy_order_by_not_author(self, client, user, order, url):
        headers = self.take_headers(user.token)

        response = client.delete(url + f'{order.id}/', headers=headers)

        assert response.status_code == 403

    @pytest.mark.django_db
    def test_destroy_by_admin(self, client, admin, order, url):
        headers = self.take_headers(admin.token)

        response = client.delete(url + f'{order.id}/', headers=headers)

        assert response.status_code == 204
