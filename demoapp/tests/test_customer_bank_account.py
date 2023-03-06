import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from demoapp.models import Customer, Bank, CustomerBankAccount
from pprint import pprint


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def customer():
    return Customer.objects.create(
        email='testuser@example.com',
        password='testpass',
        first_name='John',
        last_name='Doe'
    )


@pytest.fixture
def bank():
    return Bank.objects.create(
        name='Test Bank',
        logo='test_logo.png'
    )


@pytest.fixture
def account(customer, bank):
    return CustomerBankAccount.objects.create(
        customer=customer,
        bank=bank,
        account_number='1234567890',
        ifsc_code='ABCD1234567',
        is_active=True
    )


@pytest.mark.django_db
def test_create_account(client, customer, bank):
    # Ensure we can create a new account
    client.force_authenticate(user=customer)
    data = {
        "bank": str(bank.id),
        "account_number": "9876543210",
        "ifsc_code": "WXYZ7654321",
        "branch_name": "Test Branch",
        "name_as_per_bank_record": "test",
    }
    response = client.post('/api/bank/', data)
    assert response.status_code == 201
    assert response.data['bank'] == bank.id
    assert response.data['account_number'] == '9876543210'
    assert response.data['ifsc_code'] == 'WXYZ7654321'
    assert response.data['is_active'] is True


@pytest.mark.django_db
def test_create_duplicate_active_account(client, customer, bank, account):
    # Ensure we can't create a duplicate account
    client.force_authenticate(user=customer)
    data = {
        "bank": str(bank.id),
        "account_number": account.account_number,
        "ifsc_code": account.ifsc_code,
        "branch_name": "Test Branch",
        "name_as_per_bank_record": "test",
    }
    response = client.post('/api/bank/', data)
    assert response.status_code == 400
    assert 'non_field_errors' in response.data


@pytest.mark.django_db
def test_retrieve_active_account(client, customer, account):
    # Ensure we can retrieve the active account
    client.force_authenticate(user=customer)
    response = client.get('/api/bank/')
    assert response.status_code == 200
    assert response.data['bank'] == account.bank.id
    assert response.data['account_number'] == account.account_number
    assert response.data['ifsc_code'] == account.ifsc_code
    assert response.data['is_active'] == account.is_active


@pytest.mark.django_db
def test_update_account(client, customer, account):
    # Ensure we can update the active account
    client.force_authenticate(user=customer)
    data = {
        'bank': account.bank.id,
    }
    response = client.patch('/api/bank/', data)
    print(response.data)
    assert response.status_code == 200
    assert response.data['bank'] == account.bank.id
    assert response.data['account_number'] == account.account_number
    assert response.data['ifsc_code'] == account.ifsc_code
    assert response.data['is_active'] == account.is_active
