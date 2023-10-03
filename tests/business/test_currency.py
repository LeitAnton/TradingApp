import pytest
from django_dynamic_fixture import G
from rest_framework.exceptions import PermissionDenied

from business.models import Currency


class TestCurrencyViewSet:
    def take_headers(self, token):
        headers = {'Authorization': f'Bearer {token}'}
        return headers

    @pytest.fixture
    def url(self):
        url = '/api/business/currency/'
        return url

    @pytest.fixture
    def currency_payload(self):
        payload = {
            "title": "test1",
            "symbol": "TST",
            "quantity": 100,
            "price_per_quantity": 1,
        }
        return payload

    @pytest.fixture
    def currency_list(self):
        currency1 = G(Currency)
        currency2 = G(Currency)
        currency1.save()
        currency2.save()
        return [currency1, currency2]

    @pytest.mark.django_db
    def test_list_ok(self, client, user, currency_list, url):
        headers = self.take_headers(user.token)

        response = client.get(url, headers=headers)
        data = response.data

        assert len(currency_list) == len(data)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_list_permission_denied(self, client, currency_list, url):
        try:
            client.get(url)
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_create_ok(self, client, admin, currency_payload, url):
        headers = self.take_headers(admin.token)

        response = client.post(url, headers=headers, data=currency_payload)
        data = response.data

        assert response.status_code == 201
        assert data['title'] == currency_payload['title']
        assert data['symbol'] == currency_payload['symbol']
        assert data['quantity'] == currency_payload['quantity']
        assert data['price_per_quantity'] == currency_payload['price_per_quantity']

    @pytest.mark.django_db
    def test_create_permission_denied(self, client, user, currency_payload, url):
        headers = self.take_headers(user.token)

        response = client.post(url, headers=headers, data=currency_payload)

        assert response.status_code == 403

    @pytest.mark.django_db
    def test_create_already_exist(self, client, admin, currency, url):
        headers = self.take_headers(admin.token)

        response = client.post(url, headers=headers, data={
            'title': currency.title,
            'symbol': currency.symbol,
            'quantity': currency.quantity,
            'price_per_quantity': currency.price_per_quantity
        })
        currencies = Currency.objects.all()

        assert response.status_code == 400
        assert currency in currencies

    @pytest.mark.django_db
    def test_create_required_field(self, client, admin, url):
        headers = self.take_headers(admin.token)

        response = client.post(url, headers=headers)

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_retrieve_ok(self, client, user, currency, url):
        headers = self.take_headers(user.token)

        response = client.get(url + f'{currency.id}/', headers=headers)
        data = response.data

        assert response.status_code == 200
        assert data['title'] == currency.title
        assert data['symbol'] == currency.symbol
        assert data['quantity'] == currency.quantity
        assert data['price_per_quantity'] == currency.price_per_quantity

    @pytest.mark.django_db
    def test_retrieve_permission_denied(self, client, currency, url):
        try:
            client.get(url + f'{currency.id}/')
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False

    @pytest.mark.django_db
    def test_put_ok(self, client, admin, currency, currency_payload, url):
        headers = self.take_headers(admin.token)

        response = client.put(url + f'{currency.id}/', headers=headers, data=currency_payload)
        data = response.data

        assert response.status_code == 200
        assert data['title'] == currency_payload['title']
        assert data['symbol'] == currency_payload['symbol']
        assert data['quantity'] == currency_payload['quantity']
        assert data['price_per_quantity'] == currency_payload['price_per_quantity']

    @pytest.mark.django_db
    def test_put_not_full_update(self, client, admin, currency, url):
        headers = self.take_headers(admin.token)
        symbol = 'XXX'

        response = client.put(url + f'{currency.id}/', headers=headers, data={'symbol': symbol})

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_put_permission_denied(self, client, user, currency, currency_payload, url):
        headers = self.take_headers(user.token)

        response = client.put(url + f'{currency.id}/', headers=headers, data=currency_payload)

        assert response.status_code == 403

    @pytest.mark.django_db
    def test_patch_ok(self, client, admin, currency, url):
        headers = self.take_headers(admin.token)
        symbol = 'XXX'

        response = client.patch(url + f'{currency.id}/', headers=headers, data={'symbol': symbol})
        data = response.data

        assert response.status_code == 200
        assert data['symbol'] == symbol
        assert data['title'] == currency.title

    @pytest.mark.django_db
    def test_patch_permission_denied(self, client, user, currency, url):
        headers = self.take_headers(user.token)
        symbol = 'XXX'

        response = client.patch(url + f'{currency.id}/', headers=headers, data={'symbol': symbol})

        assert response.status_code == 403

    @pytest.mark.django_db
    def test_delete_ok(self, client, admin, currency, url):
        headers = self.take_headers(admin.token)

        response = client.delete(url + f'{currency.id}/', headers=headers)
        currencies = Currency.objects.all()

        assert response.status_code == 204
        assert currency not in currencies

    @pytest.mark.django_db
    def test_delete_permission_denied(self, client, user, currency, url):
        headers = self.take_headers(user.token)

        response = client.delete(url + f'{currency.id}/', headers=headers)
        currencies = Currency.objects.all()

        assert response.status_code == 403
        assert currency in currencies
