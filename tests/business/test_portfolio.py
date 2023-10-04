from unittest.mock import patch

import pytest
from django_dynamic_fixture import G
from rest_framework.exceptions import PermissionDenied

from business.models import Portfolio


class TestPortfolioViewSet:
    def take_headers(self, token):
        return {'Authorization': f'Bearer {token}'}

    @pytest.fixture
    def url(self):
        return '/api/business/portfolio/'

    @pytest.fixture
    def user_s_portfolio_list(self, user):
        return G(Portfolio, user=user, n=2)

    @pytest.fixture
    def portfolio_list(self):
        return G(Portfolio, n=2)

    @pytest.mark.django_db
    def test_list_mock_on_queryset(self, client, user, user_s_portfolio_list, portfolio_list, url):
        headers = self.take_headers(user.token)

        with patch('business.views.get_own_if_not_a_stuff') as mock_function:
            mock_function.return_value = Portfolio.objects.all()
            response = client.get(url, headers=headers)
            pk_list = [portfolio['pk'] for portfolio in response.data]

            assert response.status_code == 200
            assert all(portfolio.id in pk_list for portfolio in user_s_portfolio_list)
            assert all(portfolio.id in pk_list for portfolio in portfolio_list)

    @pytest.mark.django_db
    def test_list_without_mock(self, client, user, user_s_portfolio_list, portfolio_list, url):
        headers = self.take_headers(user.token)

        response = client.get(url, headers=headers)
        pk_list = [portfolio['pk'] for portfolio in response.data]

        assert response.status_code == 200
        assert all(portfolio.id in pk_list for portfolio in user_s_portfolio_list)
        assert all(portfolio.id not in pk_list for portfolio in portfolio_list)

    @pytest.mark.django_db
    def test_list_permission_denied(self, client, url):
        try:
            client.get(url)
        except PermissionDenied as error:
            assert error.status_code == 403
        else:
            assert False
